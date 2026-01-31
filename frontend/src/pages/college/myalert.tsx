import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import {
  ArrowLeft,
  Bell,
  Calendar,
  CheckCircle,
  Clock,
  ExternalLink,
  GraduationCap,
  Mail,
  Search,
} from 'lucide-react';
import type { Alert } from '@/types/college';

// Group alerts by entrance_exam_id
interface GroupedAlerts {
  exam_id: number;
  college_name: string;
  degree: string;
  branch?: string;
  alerts: Alert[];
}

const formatAlertType = (type: string): string => {
  const typeMap: Record<string, string> = {
    registration_start: 'Registration Start',
    registration_3days: '3 Days Before Deadline',
    registration_last: 'Last Day Reminder',
    exam_1day: '1 Day Before Exam',
  };
  return typeMap[type] || type;
};

const formatDate = (dateStr: string): string => {
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
};

const MyAlerts = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  const [email, setEmail] = useState(user?.email || '');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasFetched, setHasFetched] = useState(false);

  const fetchAlerts = async (searchEmail: string) => {
    if (!searchEmail.trim()) {
      toast({
        title: 'Email Required',
        description: 'Please enter your email to view alerts.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    const res = await api.get<Alert[] | { alerts: Alert[] }>(
      `/admission-alerts/my-alerts?email=${encodeURIComponent(searchEmail)}`
    );

    if (res.data) {
      // Handle both array and object with alerts property
      const alertsData = Array.isArray(res.data) ? res.data : (res.data.alerts || []);
      setAlerts(alertsData);
    } else if (res.error) {
      toast({
        title: 'Failed to Fetch Alerts',
        description: res.error || 'Could not load alerts.',
        variant: 'destructive',
      });
    }
    setIsLoading(false);
    setHasFetched(true);
  };

  // Auto-fetch if user email is available
  useEffect(() => {
    if (user?.email) {
      fetchAlerts(user.email);
    }
  }, [user?.email]);

  // Group alerts by exam
  const groupedAlerts: GroupedAlerts[] = (Array.isArray(alerts) ? alerts : []).reduce((acc: GroupedAlerts[], alert) => {
    const existing = acc.find((g) => g.exam_id === alert.entrance_exam_id);
    if (existing) {
      existing.alerts.push(alert);
    } else {
      acc.push({
        exam_id: alert.entrance_exam_id,
        college_name: alert.college_name || 'Unknown College',
        degree: alert.degree || '',
        branch: alert.branch,
        alerts: [alert],
      });
    }
    return acc;
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center gap-4 px-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-2">
            <Bell className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">My Admission Alerts</span>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-3xl">
        {/* Email Search */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Mail className="h-5 w-5" />
              Check Your Alerts
            </CardTitle>
            <CardDescription>
              Enter the email you used when setting up alerts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    fetchAlerts(email);
                  }
                }}
                className="flex-1"
              />
              <Button onClick={() => fetchAlerts(email)} disabled={isLoading}>
                {isLoading ? (
                  <Clock className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        )}

        {/* Alerts List */}
        {!isLoading && hasFetched && (
          <>
            {groupedAlerts.length > 0 ? (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {groupedAlerts.length} alert group{groupedAlerts.length !== 1 ? 's' : ''} found
                </p>

                {groupedAlerts.map((group) => (
                  <Card key={group.exam_id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-primary" />
                            {group.college_name}
                          </CardTitle>
                          <CardDescription className="flex items-center gap-2 mt-1">
                            <GraduationCap className="h-3.5 w-3.5" />
                            {group.degree}
                            {group.branch && ` • ${group.branch}`}
                          </CardDescription>
                        </div>
                        <Badge variant="outline" className="flex-shrink-0">
                          {group.alerts.filter((a) => !a.is_sent).length} pending
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {group.alerts.map((alert) => (
                          <div
                            key={alert.id}
                            className={`flex items-center justify-between p-2 rounded-lg ${
                              alert.is_sent ? 'bg-muted/50' : 'bg-primary/5'
                            }`}
                          >
                            <div className="flex items-center gap-2">
                              {alert.is_sent ? (
                                <CheckCircle className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <Clock className="h-4 w-4 text-primary" />
                              )}
                              <span className={`text-sm ${alert.is_sent ? 'text-muted-foreground' : ''}`}>
                                {formatAlertType(alert.alert_type)}
                              </span>
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {formatDate(alert.alert_date)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="p-8 text-center">
                <Bell className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-lg font-medium mb-2">No Alerts Found</p>
                <p className="text-muted-foreground mb-4">
                  You haven't set any admission alerts yet.
                </p>
                <Button onClick={() => navigate('/college-finder')}>
                  <Search className="h-4 w-4 mr-2" />
                  Find Colleges & Set Alerts
                </Button>
              </Card>
            )}
          </>
        )}

        {/* Initial State */}
        {!isLoading && !hasFetched && !user?.email && (
          <Card className="p-8 text-center">
            <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              Enter your email above to view your alerts
            </p>
          </Card>
        )}
      </main>
    </div>
  );
};

export default MyAlerts;
