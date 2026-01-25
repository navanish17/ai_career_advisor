import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, GraduationCap, Clock, Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import type { Degree } from '@/types/career';

const STREAMS = ['science', 'commerce', 'arts'] as const;

const Degrees = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialStream = searchParams.get('stream') || 'science';
  
  const [activeStream, setActiveStream] = useState(initialStream);
  const [degrees, setDegrees] = useState<Degree[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDegrees = async () => {
      setIsLoading(true);
      try {
        const response = await api.get(`/api/degree/api/degree/from-stream/${activeStream}`);
        setDegrees(response.data);
      } catch (error: any) {
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Failed to load degrees',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchDegrees();
  }, [activeStream]);

  const handleDegreeClick = (degreeId: number) => {
    navigate(`/branches/${degreeId}`);
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-6 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Explore Degrees</h1>
            <p className="text-muted-foreground">Find the right degree for your career path</p>
          </div>
        </div>

        <Tabs value={activeStream} onValueChange={setActiveStream} className="mb-6">
          <TabsList className="grid w-full grid-cols-3">
            {STREAMS.map((stream) => (
              <TabsTrigger key={stream} value={stream} className="capitalize">
                {stream}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : degrees.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <GraduationCap className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No degrees found for this stream</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {degrees.map((degree) => (
              <Card
                key={degree.id}
                className="cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
                onClick={() => handleDegreeClick(degree.id)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{degree.name}</CardTitle>
                    <Badge variant="secondary" className="capitalize">
                      {degree.stream}
                    </Badge>
                  </div>
                  <CardDescription className="line-clamp-2">
                    {degree.short_description || 'No description available'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span>{degree.duration_years || 'N/A'} years</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Degrees;
