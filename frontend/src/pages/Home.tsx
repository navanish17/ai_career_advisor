import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LogOut, User, BookOpen, Loader2, ClipboardList, Map, MessageCircle, MapPin, Bell } from 'lucide-react';
import type { Profile } from '@/types/auth';

const Home = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      const response = await api.get<Profile>('/api/profile/profile');
      if (response.data) {
        setProfile(response.data);
      }
      setIsLoading(false);
    };
    fetchProfile();
  }, []);

  const handleLogout = () => {
    logout();
  };

  const formatClassLevel = (classLevel: string | null) => {
    if (!classLevel) return 'Not set';
    return classLevel === 'class_10' ? '10th Class' : '12th Class';
  };

  return (
    <div className="min-h-screen bg-background pb-32">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Career Advisor</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Welcome, {user?.name}
            </span>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Your personalized career guidance hub
          </p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Your Profile
            </CardTitle>
            <CardDescription>Your learning preferences</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-sm text-muted-foreground">Class</p>
                  <p className="font-medium">{formatClassLevel(profile?.class_level ?? null)}</p>
                </div>
                {profile?.stream && (
                  <div>
                    <p className="text-sm text-muted-foreground">Stream</p>
                    <p className="font-medium capitalize">{profile.stream}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-muted-foreground">Location</p>
                  <p className="font-medium capitalize">{profile?.location?.replace(/_/g, ' ') || 'Not set'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Language</p>
                  <p className="font-medium capitalize">{profile?.language || 'Not set'}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card 
            className="cursor-pointer transition-all hover:shadow-lg hover:border-primary/50"
            onClick={() => navigate('/quiz')}
          >
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-2">
                <ClipboardList className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-lg">Career Quiz</CardTitle>
              <CardDescription>Discover your ideal stream based on interests</CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-dashed opacity-60">
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted mb-2">
                <Map className="h-6 w-6 text-muted-foreground" />
              </div>
              <CardTitle className="text-lg text-muted-foreground">Roadmap Generator</CardTitle>
              <CardDescription>Coming in Phase 4</CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-dashed opacity-60">
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted mb-2">
                <MapPin className="h-6 w-6 text-muted-foreground" />
              </div>
              <CardTitle className="text-lg text-muted-foreground">College Finder</CardTitle>
              <CardDescription>Coming in Phase 3</CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-dashed opacity-60">
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted mb-2">
                <Bell className="h-6 w-6 text-muted-foreground" />
              </div>
              <CardTitle className="text-lg text-muted-foreground">Admission Alerts</CardTitle>
              <CardDescription>Coming in Phase 3</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </main>

      <div className="fixed bottom-0 left-0 right-0 border-t bg-background p-4">
        <div className="container mx-auto max-w-4xl">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <MessageCircle className="h-6 w-6 text-primary" />
                <div className="flex-1">
                  <p className="font-medium">AI Career Assistant</p>
                  <p className="text-sm text-muted-foreground">Ask me anything about careers</p>
                </div>
                <Button disabled>
                  Coming in Phase 5
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Home;
