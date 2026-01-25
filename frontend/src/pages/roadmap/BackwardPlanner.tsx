import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import RoadmapTimeline from '@/components/RoadmapTimeline';
import { 
  BookOpen, 
  ArrowLeft, 
  Target, 
  Lightbulb,
  Loader2,
  Sparkles
} from 'lucide-react';
import type { BackwardRoadmapRequest, BackwardRoadmapResponse } from '@/types/roadmap';

const careerTemplates = [
  'Software Engineer',
  'Doctor',
  'CA',
  'Data Scientist',
  'IAS Officer',
  'Investment Banker',
  'Architect',
  'Lawyer'
];

const BackwardPlanner = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  
  const initialGoal = (location.state as { careerGoal?: string })?.careerGoal || '';
  
  const [careerGoal, setCareerGoal] = useState(initialGoal);
  const [isGenerating, setIsGenerating] = useState(false);
  const [roadmapResponse, setRoadmapResponse] = useState<BackwardRoadmapResponse | null>(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [roadmapName, setRoadmapName] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleGenerate = async () => {
    if (!careerGoal.trim()) {
      toast({
        title: 'Please enter your career goal',
        description: 'Tell us what you want to become',
        variant: 'destructive'
      });
      return;
    }

    setIsGenerating(true);
    const request: BackwardRoadmapRequest = { career_goal: careerGoal };
    
    const response = await api.post<BackwardRoadmapResponse>('/backward-planner/generate', request);
    
    if (response.data) {
      setRoadmapResponse(response.data);
      setRoadmapName(`${response.data.roadmap.normalized_career} Path`);
    } else {
      toast({
        title: 'Generation failed',
        description: response.error || 'Could not generate roadmap',
        variant: 'destructive'
      });
    }
    setIsGenerating(false);
  };

  const handleTemplateClick = (template: string) => {
    setCareerGoal(`I want to become a ${template}`);
  };

  const handleSave = async () => {
    if (!roadmapName.trim() || !roadmapResponse) return;

    setIsSaving(true);
    
    toast({
      title: 'Roadmap saved!',
      description: 'Feature coming soon - backend endpoint needed',
      variant: 'default'
    });
    setShowSaveDialog(false);
    
    setIsSaving(false);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Career Advisor</span>
          </div>
          <Button variant="ghost" onClick={() => navigate('/roadmap')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Roadmap Hub
          </Button>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-4xl">
        {!roadmapResponse ? (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Target className="h-8 w-8 text-primary" />
                What do you want to become?
              </h1>
              <p className="text-muted-foreground mt-1">
                Describe your dream career and we'll create your personalized path
              </p>
            </div>

            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">Your Career Goal</CardTitle>
                <CardDescription>
                  Be specific! Include your current education, interests, and target companies for better results.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="e.g., I want to become a Machine Learning Engineer at Google. I'm currently in Class 12 Science stream and love mathematics and programming."
                  value={careerGoal}
                  onChange={(e) => setCareerGoal(e.target.value)}
                  className="min-h-[120px]"
                />
                
                <div className="flex items-start gap-2 p-3 bg-muted rounded-lg">
                  <Lightbulb className="h-5 w-5 text-amber-500 mt-0.5" />
                  <p className="text-sm text-muted-foreground">
                    <strong>Tip:</strong> The more details you provide about your current situation and goals, 
                    the more personalized your roadmap will be.
                  </p>
                </div>

                <Button 
                  className="w-full" 
                  size="lg"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating Your Roadmap...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate My Roadmap
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-3">Quick Templates</h3>
              <div className="flex flex-wrap gap-2">
                {careerTemplates.map((template) => (
                  <Badge 
                    key={template}
                    variant="outline" 
                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors py-2 px-3"
                    onClick={() => handleTemplateClick(template)}
                  >
                    {template}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="mb-6">
              <Button variant="outline" onClick={() => setRoadmapResponse(null)}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Create Another Roadmap
              </Button>
            </div>

            <RoadmapTimeline 
              roadmapData={roadmapResponse.roadmap}
              source={roadmapResponse.source}
              onSave={() => setShowSaveDialog(true)}
            />
          </>
        )}

        <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Save Your Roadmap</DialogTitle>
            </DialogHeader>
            <div className="py-4">
              <label className="text-sm font-medium">Roadmap Name</label>
              <Input
                value={roadmapName}
                onChange={(e) => setRoadmapName(e.target.value)}
                placeholder="e.g., My Software Engineer Journey"
                className="mt-2"
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving || !roadmapName.trim()}>
                {isSaving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Save Roadmap
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
};

export default BackwardPlanner;
