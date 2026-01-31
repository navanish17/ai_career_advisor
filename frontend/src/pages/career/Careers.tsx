import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Briefcase, TrendingUp, DollarSign, Loader2, Building2, Lightbulb, GraduationCap, Target, Map } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import type { Career, CareerInsight } from '@/types/career';

const Careers = () => {
  const navigate = useNavigate();
  const { branchId } = useParams<{ branchId: string }>();
  
  const [careers, setCareers] = useState<Career[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCareer, setSelectedCareer] = useState<Career | null>(null);
  const [insight, setInsight] = useState<CareerInsight | null>(null);
  const [isLoadingInsight, setIsLoadingInsight] = useState(false);

  useEffect(() => {
    const fetchCareers = async () => {
      setIsLoading(true);
      const response = await api.get<Career[]>(`/api/career/from-branch/${branchId}`);
      
      if (response.data) {
        setCareers(response.data);
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Failed to load careers',
          variant: 'destructive',
        });
      }
      setIsLoading(false);
    };
    
    if (branchId) {
      fetchCareers();
    }
  }, [branchId]);

  const handleCareerClick = async (career: Career) => {
    setSelectedCareer(career);
    setIsLoadingInsight(true);
    
    const response = await api.get<CareerInsight>(`/api/career-insight/${career.id}`);
    if (response.data) {
      setInsight(response.data);
    }
    setIsLoadingInsight(false);
  };

  const closeDialog = () => {
    setSelectedCareer(null);
    setInsight(null);
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Career Options</h1>
            <p className="text-muted-foreground">Explore career paths and opportunities</p>
          </div>
        </div>

        {/* Careers Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : careers.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Briefcase className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No careers found for this specialization</p>
              <Button variant="link" onClick={() => navigate('/degrees')}>
                Explore other paths
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {careers.map((career) => (
              <Card
                key={career.id}
                className="cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
                onClick={() => handleCareerClick(career)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Briefcase className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{career.name}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <CardDescription className="line-clamp-2">
                    {career.description}
                  </CardDescription>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline" className="flex items-center gap-1">
                      <DollarSign className="h-3 w-3" />
                      {career.average_salary}
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" />
                      {career.growth_outlook}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Career Insight Dialog */}
        <Dialog open={!!selectedCareer} onOpenChange={closeDialog}>
          <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Briefcase className="h-5 w-5 text-primary" />
                </div>
                {selectedCareer?.name}
              </DialogTitle>
              <DialogDescription>{selectedCareer?.description}</DialogDescription>
            </DialogHeader>

            {isLoadingInsight ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : insight ? (
              <div className="space-y-6">
                <Separator />
                
                {/* Skills Required */}
                <div>
                  <h4 className="flex items-center gap-2 font-semibold mb-3">
                    <Lightbulb className="h-4 w-4 text-primary" />
                    Skills Required
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {insight.skills_required.map((skill, index) => (
                      <Badge key={index} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>

                {/* Education Path */}
                <div>
                  <h4 className="flex items-center gap-2 font-semibold mb-2">
                    <GraduationCap className="h-4 w-4 text-primary" />
                    Education Path
                  </h4>
                  <p className="text-sm text-muted-foreground">{insight.education_path}</p>
                </div>

                {/* Job Roles */}
                <div>
                  <h4 className="flex items-center gap-2 font-semibold mb-3">
                    <Target className="h-4 w-4 text-primary" />
                    Common Job Roles
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {insight.job_roles.map((role, index) => (
                      <Badge key={index} variant="outline">{role}</Badge>
                    ))}
                  </div>
                </div>

                {/* Top Companies */}
                <div>
                  <h4 className="flex items-center gap-2 font-semibold mb-3">
                    <Building2 className="h-4 w-4 text-primary" />
                    Top Companies
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {insight.top_companies.map((company, index) => (
                      <Badge key={index}>{company}</Badge>
                    ))}
                  </div>
                </div>

                {/* Future Prospects */}
                <div>
                  <h4 className="flex items-center gap-2 font-semibold mb-2">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    Future Prospects
                  </h4>
                  <p className="text-sm text-muted-foreground">{insight.future_prospects}</p>
                </div>

                <Separator />
                
                <DialogFooter>
                  <Button 
                    className="w-full"
                    onClick={() => navigate('/roadmap/forward', { 
                      state: { careerId: selectedCareer?.id, careerName: selectedCareer?.name } 
                    })}
                  >
                    <Map className="h-4 w-4 mr-2" />
                    Generate Roadmap for This Career
                  </Button>
                </DialogFooter>
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-4">
                No detailed insights available
              </p>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default Careers;
