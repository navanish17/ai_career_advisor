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
  const [renderError, setRenderError] = useState<string | null>(null);

  const initialGoal = (location.state as { careerGoal?: string })?.careerGoal || '';

  const [careerGoal, setCareerGoal] = useState(initialGoal);
  const [isGenerating, setIsGenerating] = useState(false);
  const [roadmapResponse, setRoadmapResponse] = useState<BackwardRoadmapResponse | null>(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [roadmapName, setRoadmapName] = useState('');
  const [isSaving, setIsSaving] = useState(false);


  const handleGenerate = async () => {
    try {
      const trimmedGoal = careerGoal.trim();

      if (!trimmedGoal) {
        toast({
          title: 'Please enter your career goal',
          description: 'Tell us what you want to become',
          variant: 'destructive'
        });
        return;
      }

      if (trimmedGoal.length < 3) {
        toast({
          title: 'Career goal too short',
          description: 'Please provide at least 3 characters',
          variant: 'destructive'
        });
        return;
      }

      setIsGenerating(true);

      const request = {
        career_goal: trimmedGoal
      };

      console.log('Sending request:', request);

      const response = await api.post('/backward-planner/generate', request);

      console.log('Full API Response:', response);
      console.log('Response status:', response.status);
      console.log('Response data:', response.data);
      console.log('Response error:', response.error);

      if (response.error) {
        console.error('API returned error:', response.error);

        const errorObj = response.error as any;
        const errorMessage = typeof errorObj === 'string'
          ? errorObj
          : errorObj.message || errorObj.error || JSON.stringify(errorObj);

        toast({
          title: 'Generation failed',
          description: errorMessage,
          variant: 'destructive'
        });
        setIsGenerating(false);
        return;
      }

      if (!response.data) {
        console.error('No data in response');
        toast({
          title: 'Generation failed',
          description: 'No data received from server',
          variant: 'destructive'
        });
        setIsGenerating(false);
        return;
      }

      const apiResponse = response.data as any;

      if (apiResponse.success === false) {
        console.error('API returned success=false:', apiResponse);
        toast({
          title: 'Generation failed',
          description: apiResponse.message || apiResponse.error || 'Could not generate roadmap',
          variant: 'destructive'
        });
        setIsGenerating(false);
        return;
      }

      if (apiResponse.roadmap) {
        console.log('Valid roadmap received');
        setRoadmapResponse(apiResponse as BackwardRoadmapResponse);
        toast({
          title: 'Success!',
          description: 'Your personalized roadmap is ready',
        });
      } else {
        console.error('No roadmap in response:', apiResponse);
        toast({
          title: 'Generation failed',
          description: 'Invalid response format',
          variant: 'destructive'
        });
      }

      setIsGenerating(false);

    } catch (error: any) {
      console.error('Exception during generation:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);

      const errorMessage = error.response?.data?.detail
        || error.response?.data?.message
        || error.message
        || 'An unexpected error occurred';

      toast({
        title: 'Error generating roadmap',
        description: errorMessage,
        variant: 'destructive'
      });

      setIsGenerating(false);
    }
  };


  const buildDynamicSteps = (raw: any): any[] => {
    const steps: any[] = [];
    let stepNumber = 1;


    if (raw.timeline?.class_10) {
      steps.push({
        step_number: stepNumber++,
        type: "education",
        title: "Class 10 Foundation",
        description: raw.timeline.class_10,
        duration: "1 year",
        focus_areas: ["Build strong academic foundation", "General awareness"],
        key_exams: ["Class 10 Board Exams"],
        skills: [],
        projects: [],
        top_colleges: [],
        top_1_percent_tips: []
      });
    }


    if (raw.timeline?.class_11_12 || raw.stream_recommendation) {
      const streamInfo = raw.stream_recommendation?.class_11_12 || "Any stream";
      const streamReason = raw.stream_recommendation?.reason || raw.timeline?.class_11_12 || "Choose stream based on interest";

      steps.push({
        step_number: stepNumber++,
        type: "education",
        title: `Class 11-12 - ${streamInfo}`,
        description: streamReason,
        duration: "2 years",
        focus_areas: raw.stream_recommendation?.alternatives || [],
        key_exams: ["Class 12 Board Exams"],
        skills: [],
        projects: [],
        top_colleges: [],
        top_1_percent_tips: raw.stream_recommendation?.reason ? [raw.stream_recommendation.reason] : []
      });
    }


    if (raw.required_education || raw.timeline?.graduation_year_1_2) {
      const degreeTitle = raw.required_education?.preferred_degree || raw.required_education?.minimum_degree || "Bachelor's Degree";
      const description = raw.timeline?.graduation_year_1_2 ||
        raw.timeline?.graduation_year_3 ||
        raw.required_education?.specialization ||
        "Complete your undergraduate degree with good academic standing";

      steps.push({
        step_number: stepNumber++,
        type: "education",
        title: `Graduation - ${degreeTitle}`,
        description: description,
        duration: "3-4 years",
        focus_areas: raw.required_education?.degree_options?.slice(0, 5) || [],
        key_exams: [],
        skills: raw.skills_required?.slice(0, 5).map((s: any) => s.skill) || [],
        projects: raw.projects_to_build || [],
        top_colleges: raw.top_colleges?.slice(0, 5).map((c: any) => c.name) || [],
        top_1_percent_tips: raw.required_education?.specialization ? [raw.required_education.specialization] : []
      });
    }


    if (raw.timeline?.post_graduation_phase_1 || raw.timeline?.post_graduation_phase_2) {
      const description = raw.timeline?.post_graduation_phase_1 || raw.timeline?.post_graduation_phase_2;

      steps.push({
        step_number: stepNumber++,
        type: "education",
        title: "Post-Graduation / Preparation Phase",
        description: description,
        duration: "1-3 years",
        focus_areas: raw.entrance_exams?.map((e: any) => e.when_to_prepare) || [],
        key_exams: raw.entrance_exams?.map((e: any) => e.exam_name) || [],
        skills: raw.skills_required?.slice(0, 3).map((s: any) => s.skill) || [],
        projects: [],
        top_colleges: [],
        top_1_percent_tips: raw.certifications?.map((c: any) => c.name) || []
      });
    }


    if (raw.entrance_exams && raw.entrance_exams.length > 0 && !raw.timeline?.post_graduation_phase_1) {
      raw.entrance_exams.forEach((exam: any, index: number) => {
        if (index === 0) {
          steps.push({
            step_number: stepNumber++,
            type: "exam",
            title: exam.exam_name,
            description: exam.for || "Prepare for and clear this entrance exam",
            duration: exam.when_to_prepare?.includes("year") ? "1-2 years" : "6-12 months",
            focus_areas: [exam.when_to_prepare || "Intensive preparation required"],
            key_exams: raw.entrance_exams.map((e: any) => e.exam_name),
            skills: raw.skills_required?.slice(0, 3).map((s: any) => s.skill) || [],
            projects: [],
            top_colleges: [],
            top_1_percent_tips: exam.difficulty ? [`Difficulty: ${exam.difficulty}`] : []
          });
        }
      });
    }


    if (raw.internships && raw.internships.length > 0) {
      const internshipDesc = raw.internships.map((i: any) => `${i.type} (${i.duration})`).join("; ");

      steps.push({
        step_number: stepNumber++,
        type: "milestone",
        title: "Practical Training & Experience",
        description: internshipDesc,
        duration: raw.internships[0]?.duration || "Variable",
        focus_areas: raw.internships.map((i: any) => i.type),
        key_exams: [],
        skills: raw.skills_required?.map((s: any) => s.skill) || [],
        projects: [],
        top_colleges: [],
        top_1_percent_tips: []
      });
    }


    steps.push({
      step_number: stepNumber++,
      type: "career",
      title: `Career as ${raw.normalized_career}`,
      description: raw.career_description || `Begin your professional journey as ${raw.normalized_career}`,
      duration: "Lifelong Career",
      focus_areas: raw.skills_required?.map((s: any) => `${s.skill} (${s.level})`) || [],
      key_exams: [],
      skills: raw.skills_required?.map((s: any) => s.skill) || [],
      projects: raw.projects_to_build || [],
      top_colleges: [],
      top_1_percent_tips: [
        ...(raw.career_prospects?.average_salary ? [`Starting: ${raw.career_prospects.average_salary}`] : []),
        ...(raw.career_prospects?.experienced_salary ? [`Experienced: ${raw.career_prospects.experienced_salary}`] : []),
        ...(raw.career_prospects?.growth_rate ? [`Growth: ${raw.career_prospects.growth_rate}`] : [])
      ]
    });


    return steps;
  };


  const handleTemplateClick = (template: string) => {
    setCareerGoal(`I want to become a ${template}`);
  };


  const handleSave = async () => {
    if (!roadmapName.trim() || !roadmapResponse) return;


    setIsSaving(true);
    try {
      const saveRequest = {
        name: roadmapName,
        type: 'backward',
        career_goal: careerGoal,
        roadmap_data: roadmapResponse.roadmap
      };


      console.log('Sending backward planner save request:', saveRequest);
      const response = await api.post('/api/roadmap/save', saveRequest);
      console.log('Save response:', response);

      if (response.data) {
        toast({
          title: 'Success!',
          description: 'Roadmap saved to your profile'
        });
        setShowSaveDialog(false);
      } else {
        console.error('Save error:', response.error);
        toast({
          title: 'Save failed',
          description: response.error || 'Could not save roadmap',
          variant: 'destructive'
        });
      }
    } catch (error) {
      console.error('Exception saving roadmap:', error);
      toast({
        title: 'Error',
        description: 'Failed to save roadmap',
        variant: 'destructive'
      });
    } finally {
      setIsSaving(false);
    }
  };


  return (
    <div className="min-h-screen bg-background">
      {renderError && (
        <div className="bg-destructive/10 border border-destructive text-destructive p-4 m-4 rounded">
          <p className="font-semibold">Error: {renderError}</p>
          <Button
            onClick={() => setRenderError(null)}
            variant="outline"
            size="sm"
            className="mt-2"
          >
            Dismiss
          </Button>
        </div>
      )}

      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Career Pilot</span>
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


            {roadmapResponse && roadmapResponse.roadmap ? (
              <RoadmapTimeline
                roadmapData={roadmapResponse.roadmap}
                source={roadmapResponse.source}
                onSave={() => setShowSaveDialog(true)}
              />
            ) : (
              <Card className="p-6 border-destructive">
                <p className="text-destructive font-semibold mb-4">Unable to load roadmap data</p>
                <p className="text-muted-foreground mb-4">Debug Information:</p>
                <pre className="p-4 bg-muted rounded text-xs overflow-auto max-h-96 border">
                  {JSON.stringify({
                    hasResponse: !!roadmapResponse,
                    hasRoadmap: !!roadmapResponse?.roadmap,
                    data: roadmapResponse
                  }, null, 2)}
                </pre>
                <Button
                  onClick={() => setRoadmapResponse(null)}
                  className="mt-4"
                >
                  Try Again
                </Button>
              </Card>
            )}
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
