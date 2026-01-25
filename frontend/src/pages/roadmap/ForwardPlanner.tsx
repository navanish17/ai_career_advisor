import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { 
  BookOpen, 
  ArrowLeft, 
  ArrowRight,
  Loader2,
  GraduationCap,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import type { Profile } from '@/types/auth';
import type { ForwardRoadmapRequest, ForwardRoadmapResponse } from '@/types/roadmap';

// These types should match your backend response
interface Degree {
  id: number;
  name: string;
  stream: string;
  short_description?: string | null;
  duration_years?: number | null;
  eligibility?: string | null;
}

interface Branch {
  id: number;
  name: string;
  degree_id: number;
}

interface Career {
  id: number;
  name: string;
  description?: string | null;
  market_trend?: string | null;
  salary_range?: string | null;
}

const steps = [
  { id: 1, title: 'Class Level' },
  { id: 2, title: 'Stream' },
  { id: 3, title: 'Degree' },
  { id: 4, title: 'Specialization' },
  { id: 5, title: 'Career' },
];

const ForwardPlanner = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  
  const preSelectedCareer = (location.state as { careerId?: number; careerName?: string })?.careerId;
  
  const [currentStep, setCurrentStep] = useState(1);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  
  // Selections
  const [classLevel, setClassLevel] = useState<string>('');
  const [stream, setStream] = useState<string>('');
  const [selectedDegreeId, setSelectedDegreeId] = useState<number | null>(null);
  const [selectedBranchId, setSelectedBranchId] = useState<number | null>(null);
  const [selectedCareerId, setSelectedCareerId] = useState<number | null>(preSelectedCareer || null);
  
  // Data
  const [degrees, setDegrees] = useState<Degree[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [careers, setCareers] = useState<Career[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(false);
  
  // Result
  const [roadmapId, setRoadmapId] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Load profile
  useEffect(() => {
    const fetchProfile = async () => {
      const response = await api.get<Profile>('/api/profile/profile');
      if (response.data) {
        setProfile(response.data);
        if (response.data.class_level) {
          setClassLevel(response.data.class_level);
        }
        if (response.data.stream) {
          setStream(response.data.stream);
        }
      }
      setIsLoadingProfile(false);
    };
    fetchProfile();
  }, []);

  // Load degrees when stream is selected
  useEffect(() => {
    if (stream) {
      const fetchDegrees = async () => {
        setIsLoadingData(true);
        const response = await api.get<Degree[]>(`/api/degree/api/degree/from-stream/${stream}`);
        if (response.data) {
          setDegrees(response.data);
        }
        setIsLoadingData(false);
      };
      fetchDegrees();
    }
  }, [stream]);

  // Load branches when degree is selected
  useEffect(() => {
    if (selectedDegreeId) {
      const fetchBranches = async () => {
        setIsLoadingData(true);
        const response = await api.get<Branch[]>(`/api/branch/from-degree/${selectedDegreeId}`);
        if (response.data) {
          setBranches(response.data);
        }
        setIsLoadingData(false);
      };
      fetchBranches();
    }
  }, [selectedDegreeId]);

  // Load careers when branch is selected
  useEffect(() => {
    if (selectedBranchId) {
      const fetchCareers = async () => {
        setIsLoadingData(true);
        const response = await api.get<Career[]>(`/api/career/from-branch/${selectedBranchId}`);
        if (response.data) {
          setCareers(response.data);
        }
        setIsLoadingData(false);
      };
      fetchCareers();
    }
  }, [selectedBranchId]);

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1: return !!classLevel;
      case 2: return !!stream;
      case 3: return !!selectedDegreeId;
      case 4: return !!selectedBranchId;
      case 5: return !!selectedCareerId;
      default: return false;
    }
  };

  const handleGenerate = async () => {
    if (!selectedDegreeId || !selectedBranchId || !selectedCareerId) {
      toast({
        title: 'Missing selections',
        description: 'Please complete all steps',
        variant: 'destructive'
      });
      return;
    }

    setIsGenerating(true);
    const request: ForwardRoadmapRequest = {
      degree_id: selectedDegreeId,
      branch_id: selectedBranchId,
      career_id: selectedCareerId
    };

    const response = await api.post<ForwardRoadmapResponse>('/api/roadmap/roadmap/generate', request);
    
    if (response.data) {
      setRoadmapId(response.data.roadmap_id);
      toast({
        title: 'Success!',
        description: response.data.message
      });
      // Navigate to view roadmap page
      navigate(`/roadmap/view/${response.data.roadmap_id}`);
    } else {
      toast({
        title: 'Generation failed',
        description: response.error || 'Could not generate roadmap',
        variant: 'destructive'
      });
    }
    setIsGenerating(false);
  };

  const renderStepContent = () => {
    if (isLoadingData) {
      return (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      );
    }

    switch (currentStep) {
      case 1:
        return (
          <RadioGroup value={classLevel} onValueChange={setClassLevel}>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer">
                <RadioGroupItem value="class_10" id="class_10" />
                <Label htmlFor="class_10" className="flex-1 cursor-pointer">
                  <div className="font-medium">Class 10</div>
                  <div className="text-sm text-muted-foreground">Currently in 10th or completed</div>
                </Label>
                {profile?.class_level === 'class_10' && (
                  <span className="text-xs text-primary">(Your profile)</span>
                )}
              </div>
              <div className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer">
                <RadioGroupItem value="class_12" id="class_12" />
                <Label htmlFor="class_12" className="flex-1 cursor-pointer">
                  <div className="font-medium">Class 12</div>
                  <div className="text-sm text-muted-foreground">Currently in 12th or completed</div>
                </Label>
                {profile?.class_level === 'class_12' && (
                  <span className="text-xs text-primary">(Your profile)</span>
                )}
              </div>
            </div>
          </RadioGroup>
        );

      case 2:
        return (
          <RadioGroup value={stream} onValueChange={setStream}>
            <div className="space-y-3">
              {['science', 'commerce', 'arts'].map((s) => (
                <div key={s} className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer">
                  <RadioGroupItem value={s} id={s} />
                  <Label htmlFor={s} className="flex-1 cursor-pointer capitalize font-medium">
                    {s}
                  </Label>
                  {profile?.stream === s && (
                    <span className="text-xs text-primary">(Your profile)</span>
                  )}
                </div>
              ))}
            </div>
          </RadioGroup>
        );

      case 3:
        return (
          <RadioGroup 
            value={selectedDegreeId?.toString() || ''} 
            onValueChange={(v) => {
              setSelectedDegreeId(parseInt(v));
              setSelectedBranchId(null);
              setSelectedCareerId(null);
            }}
          >
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {degrees.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No degrees found for this stream</p>
              ) : (
                degrees.map((degree) => (
                  <div key={degree.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer">
                    <RadioGroupItem value={degree.id.toString()} id={`degree-${degree.id}`} className="mt-1" />
                    <Label htmlFor={`degree-${degree.id}`} className="flex-1 cursor-pointer">
                      <div className="font-medium">{degree.name}</div>
                      {degree.short_description && (
                        <div className="text-sm text-muted-foreground">{degree.short_description}</div>
                      )}
                      {degree.duration_years && (
                        <div className="text-xs text-muted-foreground mt-1">Duration: {degree.duration_years} years</div>
                      )}
                    </Label>
                  </div>
                ))
              )}
            </div>
          </RadioGroup>
        );

      case 4:
        return (
          <RadioGroup 
            value={selectedBranchId?.toString() || ''} 
            onValueChange={(v) => {
              setSelectedBranchId(parseInt(v));
              setSelectedCareerId(null);
            }}
          >
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {branches.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No branches found for this degree</p>
              ) : (
                branches.map((branch) => (
                  <div key={branch.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer">
                    <RadioGroupItem value={branch.id.toString()} id={`branch-${branch.id}`} className="mt-1" />
                    <Label htmlFor={`branch-${branch.id}`} className="flex-1 cursor-pointer">
                      <div className="font-medium">{branch.name}</div>
                    </Label>
                  </div>
                ))
              )}
            </div>
          </RadioGroup>
        );

      case 5:
        return (
          <RadioGroup 
            value={selectedCareerId?.toString() || ''} 
            onValueChange={(v) => setSelectedCareerId(parseInt(v))}
          >
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {careers.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No careers found for this branch</p>
              ) : (
                careers.map((career) => (
                  <div key={career.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer">
                    <RadioGroupItem value={career.id.toString()} id={`career-${career.id}`} className="mt-1" />
                    <Label htmlFor={`career-${career.id}`} className="flex-1 cursor-pointer">
                      <div className="font-medium">{career.name}</div>
                      {career.description && (
                        <div className="text-sm text-muted-foreground">{career.description}</div>
                      )}
                      {career.salary_range && (
                        <div className="text-xs text-muted-foreground mt-1">Salary: {career.salary_range}</div>
                      )}
                    </Label>
                  </div>
                ))
              )}
            </div>
          </RadioGroup>
        );

      default:
        return null;
    }
  };

  if (isLoadingProfile) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

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

      <main className="container mx-auto p-4 max-w-3xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <GraduationCap className="h-8 w-8 text-primary" />
            Forward Planning
          </h1>
          <p className="text-muted-foreground mt-1">
            Build your career path step by step
          </p>
        </div>

        {/* Progress */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            {steps.map((step) => (
              <div 
                key={step.id}
                className={`flex items-center gap-1 text-sm ${
                  step.id === currentStep 
                    ? 'text-primary font-medium' 
                    : step.id < currentStep 
                      ? 'text-green-600' 
                      : 'text-muted-foreground'
                }`}
              >
                {step.id < currentStep ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <span className={`h-5 w-5 rounded-full flex items-center justify-center text-xs ${
                    step.id === currentStep ? 'bg-primary text-primary-foreground' : 'bg-muted'
                  }`}>
                    {step.id}
                  </span>
                )}
                <span className="hidden sm:inline">{step.title}</span>
              </div>
            ))}
          </div>
          <Progress value={(currentStep / 5) * 100} className="h-2" />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{steps[currentStep - 1].title}</CardTitle>
            <CardDescription>
              {currentStep === 1 && 'What is your current education level?'}
              {currentStep === 2 && 'Which stream are you interested in?'}
              {currentStep === 3 && 'Select your preferred degree'}
              {currentStep === 4 && 'Choose your specialization'}
              {currentStep === 5 && 'Select your target career'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {renderStepContent()}

            <div className="flex justify-between mt-6">
              <Button 
                variant="outline" 
                onClick={handleBack}
                disabled={currentStep === 1}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              
              {currentStep < 5 ? (
                <Button onClick={handleNext} disabled={!canProceed()}>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button 
                  onClick={handleGenerate} 
                  disabled={!canProceed() || isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Roadmap
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default ForwardPlanner;
