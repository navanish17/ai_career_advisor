import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LogOut, User, BookOpen, Loader2, ClipboardList, GraduationCap, Map, Target, ArrowRight, FolderOpen, Building2 } from 'lucide-react';
import type { Profile } from '@/types/auth';
import type { SavedRoadmap } from '@/types/roadmap';
import ChatBot from '@/components/chat/chatbot';
import { ThemeToggle } from '@/components/theme-toggle';
const popularCareers = ['Software Engineer', 'Doctor', 'Data Scientist', 'CA', 'IAS'];

const Home = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [savedRoadmaps, setSavedRoadmaps] = useState<SavedRoadmap[]>([]);
  const [totalRoadmapsCount, setTotalRoadmapsCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [careerGoal, setCareerGoal] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      const [profileRes, roadmapsRes] = await Promise.all([
        api.get<Profile>('/api/profile/profile'),
        api.get<SavedRoadmap[]>('/api/roadmap/user')
      ]);
      if (profileRes.data) setProfile(profileRes.data);
      if (roadmapsRes.data) {
        setTotalRoadmapsCount(roadmapsRes.data.length);
        setSavedRoadmaps(roadmapsRes.data.slice(0, 2));
      }
      setIsLoading(false);
    };
    fetchData();
  }, []);

  const handleLogout = () => {
    logout();
  };

  const formatClassLevel = (classLevel: string | null) => {
    if (!classLevel) return 'Not set';
    return classLevel === 'class_10' ? '10th Class' : '12th Class';
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
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Welcome, {user?.name}
            </span>
            <ThemeToggle />
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Your personalized career guidance hub
          </p>
        </div>

        {/* User Profile Card */}
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

        {/* Career Explorer Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
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

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:border-primary/50"
            onClick={() => navigate('/degrees')}
          >
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-2">
                <GraduationCap className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-lg">Explore Degrees</CardTitle>
              <CardDescription>Browse degrees, branches and career paths</CardDescription>
            </CardHeader>
          </Card>

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:border-primary/50"
            onClick={() => navigate('/roadmap')}
          >
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-2">
                <Map className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-lg">Roadmap Generator</CardTitle>
              <CardDescription>Plan your path to success</CardDescription>
            </CardHeader>
          </Card>

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:border-primary/50"
            onClick={() => navigate('/college-finder')}
          >
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-2">
                <Building2 className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-lg">College Finder</CardTitle>
              <CardDescription>Search colleges & set admission alerts</CardDescription>
            </CardHeader>
          </Card>

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:border-primary/50 relative"
            onClick={() => navigate('/roadmap/my-roadmaps')}
          >
            <CardHeader className="pb-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-2">
                <FolderOpen className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-lg">My Roadmaps</CardTitle>
              <CardDescription>View all your saved career roadmaps</CardDescription>
              {totalRoadmapsCount > 0 && (
                <Badge className="absolute top-3 right-3" variant="secondary">
                  {totalRoadmapsCount}
                </Badge>
              )}
            </CardHeader>
          </Card>

        </div>

        {/* Roadmap Quick Access */}
        <Card className="mt-6">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Quick Roadmap
            </CardTitle>
            <CardDescription>Enter your dream career to generate a personalized path</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3 mb-4">
              <Input
                placeholder="e.g., Data Scientist at Google"
                value={careerGoal}
                onChange={(e) => setCareerGoal(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && careerGoal.trim()) {
                    navigate('/roadmap/backward', { state: { careerGoal } });
                  }
                }}
                className="flex-1"
              />
              <Button
                onClick={() => {
                  if (careerGoal.trim()) {
                    navigate('/roadmap/backward', { state: { careerGoal } });
                  } else {
                    navigate('/roadmap');
                  }
                }}
              >
                Generate
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {popularCareers.map((career) => (
                <Badge
                  key={career}
                  variant="outline"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => navigate('/roadmap/backward', { state: { careerGoal: `I want to become a ${career}` } })}
                >
                  {career}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Saved Roadmaps Preview */}
        {savedRoadmaps.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <FolderOpen className="h-5 w-5" />
                Your Roadmaps
              </h3>
              <Button variant="ghost" size="sm" onClick={() => navigate('/roadmap/my-roadmaps')}>
                View All
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
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
        )}
      </main>

      {/* Floating ChatBot */}
      <ChatBot />
    </div>
  );
};

export default Home;
