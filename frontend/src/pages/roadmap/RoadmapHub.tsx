import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import {
  BookOpen,
  ArrowLeft,
  ArrowRight,
  Target,
  Map,
  Loader2,
  FolderOpen
} from 'lucide-react';
import type { SavedRoadmap } from '@/types/roadmap';

const popularCareers = [
  'Software Engineer',
  'Doctor',
  'Data Scientist',
  'CA',
  'IAS Officer',
  'Investment Banker',
  'Architect',
  'Lawyer'
];

const RoadmapHub = () => {
  const navigate = useNavigate();
  const [careerGoal, setCareerGoal] = useState('');
  const [savedRoadmaps, setSavedRoadmaps] = useState<SavedRoadmap[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSavedRoadmaps = async () => {
      const response = await api.get<SavedRoadmap[]>('/api/roadmap/user');
      if (response.data) {
        setSavedRoadmaps(response.data.slice(0, 3)); // Show only 3 most recent
      }
      setIsLoading(false);
    };
    fetchSavedRoadmaps();
  }, []);

  const handleBackwardPlan = () => {
    if (careerGoal.trim()) {
      navigate('/roadmap/backward', { state: { careerGoal } });
    } else {
      navigate('/roadmap/backward');
    }
  };

  const handleQuickCareer = (career: string) => {
    navigate('/roadmap/backward', { state: { careerGoal: `I want to become a ${career}` } });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Career Pilot</span>
          </div>
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Map className="h-8 w-8 text-primary" />
            Roadmap Generator
          </h1>
          <p className="text-muted-foreground mt-1">
            Plan your career path with personalized guidance
          </p>
        </div>

        {/* Two Planning Options */}
        <div className="grid gap-6 md:grid-cols-2 mb-8">
          {/* Forward Planning */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 mb-2">
                <BookOpen className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle>Forward Planning</CardTitle>
              <CardDescription>
                Start from your current education and find the best path to your dream career
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Step-by-step wizard: Class → Stream → Degree → Specialization → Career
              </p>
              <Button className="w-full" onClick={() => navigate('/roadmap/forward')}>
                Start Planning
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>

          {/* Backward Planning */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 mb-2">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
              <CardTitle>"I want to become..."</CardTitle>
              <CardDescription>
                Enter your dream career and we'll create your personalized path
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input
                  placeholder="e.g., Data Scientist at Google"
                  value={careerGoal}
                  onChange={(e) => setCareerGoal(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleBackwardPlan()}
                />
                <Button
                  className="w-full"
                  variant="secondary"
                  onClick={handleBackwardPlan}
                >
                  Generate Roadmap
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Popular Career Goals */}
        <div className="mb-8">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Popular Career Goals</h3>
          <div className="flex flex-wrap gap-2">
            {popularCareers.map((career) => (
              <Badge
                key={career}
                variant="outline"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors py-2 px-3"
                onClick={() => handleQuickCareer(career)}
              >
                {career}
              </Badge>
            ))}
          </div>
        </div>

        {/* Recent Saved Roadmaps */}
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        ) : savedRoadmaps.length > 0 ? (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <FolderOpen className="h-5 w-5" />
                Your Recent Roadmaps
              </h3>
              <Button variant="ghost" size="sm" onClick={() => navigate('/roadmap/my-roadmaps')}>
                View All
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              {savedRoadmaps.map((roadmap) => (
                <Card
                  key={roadmap.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => navigate(`/roadmap/view/${roadmap.id}`)}
                >
                  <CardContent className="pt-4">
                    <div className="flex items-start gap-2">
                      <Target className="h-4 w-4 text-primary mt-1" />
                      <div>
                        <p className="font-medium line-clamp-1">{roadmap.name}</p>
                        <p className="text-xs text-muted-foreground capitalize">
                          {roadmap.type} Plan • {new Date(roadmap.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
};

export default RoadmapHub;
