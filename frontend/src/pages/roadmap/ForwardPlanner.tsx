import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
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
  CheckCircle2,
  TrendingUp,
  DollarSign,
  X,
  Star
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
  branch_id: number;
  description?: string | null;
  market_trend?: string | null;
  salary_range?: string | null;
  is_active?: boolean;
}

interface CareerInsight {
  id: number;
  career_id: number;
  skills: string[];
  internships: string[];
  projects: {
    production?: string[];
    research?: string[];
  };
  programs: string[];
  top_salary: string;
  is_active: boolean;
}

const steps = [
  { id: 1, title: 'Class Level' },
  { id: 2, title: 'Stream' },
  { id: 3, title: 'Degree' },
  { id: 4, title: 'Specialization' },
  { id: 5, title: 'Career' },
  { id: 6, title: 'Top 1%' },
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

  // ✅ NEW: Career details lazy loading
  const [careerDetailsCache, setCareerDetailsCache] = useState<Map<number, Career>>(new Map());

  // ✅ NEW: Dialog states
  const [showCareerDialog, setShowCareerDialog] = useState(false);
  const [selectedCareerForDialog, setSelectedCareerForDialog] = useState<Career | null>(null);
  const [selectedCareerInsight, setSelectedCareerInsight] = useState<CareerInsight | null>(null);
  const [loadingCareerInsight, setLoadingCareerInsight] = useState(false);
  const [loadingCareerDetails, setLoadingCareerDetailsState] = useState(false);
  const [showTop1PercentDetails, setShowTop1PercentDetails] = useState(false);
  const [top1PercentTips, setTop1PercentTips] = useState<string[]>([]);
  const [showTop1PercentDialog, setShowTop1PercentDialog] = useState(false);

  // ✅ NEW: Save dialog state
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [roadmapName, setRoadmapName] = useState('');
  const [isSavingRoadmap, setIsSavingRoadmap] = useState(false);

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
        setDegrees([]);
        setSelectedDegreeId(null);

        console.log('🔍 Fetching degrees for stream:', stream);
        console.log('📡 API URL:', `/api/degree/from-stream/${stream}`);

        try {
          const response = await api.get<Degree[]>(`/api/degree/from-stream/${stream}`);

          console.log('📦 Full Response:', response);
          console.log('📊 Response Data:', response.data);
          console.log('❌ Response Error:', response.error);

          if (response.data && Array.isArray(response.data)) {
            console.log(` Setting ${response.data.length} degrees`);
            setDegrees(response.data);

            if (response.data.length === 0) {
              toast({
                title: 'No degrees found',
                description: `No degrees available for ${stream} stream.`,
                variant: 'destructive'
              });
            }
          } else if (response.error) {
            console.error(' API Error:', response.error);
            toast({
              title: 'Error loading degrees',
              description: response.error,
              variant: 'destructive'
            });
          }
        } catch (error) {
          console.error('Exception:', error);
          toast({
            title: 'Error',
            description: 'Failed to load degrees',
            variant: 'destructive'
          });
        } finally {
          setIsLoadingData(false);
        }
      };
      fetchDegrees();
    } else {
      setDegrees([]);
    }
  }, [stream, toast]);

  // Load branches when degree is selected
  useEffect(() => {
    if (selectedDegreeId) {
      const fetchBranches = async () => {
        setIsLoadingData(true);
        setBranches([]); // Clear previous
        setSelectedBranchId(null);

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
        setCareers([]); // Clear previous
        setSelectedCareerId(null);

        const response = await api.get<Career[]>(`/api/career/from-branch/${selectedBranchId}`);
        if (response.data) {
          setCareers(response.data);
        }
        setIsLoadingData(false);
      };
      fetchCareers();
    }
  }, [selectedBranchId]);

  // ✅ NEW: Fetch career details on-demand (lazy loading with cache)
  // This is now handled by fetchFullCareerDetails in the dialog

  // ✅ NEW: Handle career click - fetch details
  // Now handled directly in the career card onClick

  const handleNext = () => {
    if (currentStep === 5 && selectedCareerId) {
      // Fetch top 1% tips when moving to step 6
      fetchTop1PercentTips(selectedCareerId);
    }

    if (currentStep < 6) {
      setCurrentStep(currentStep + 1);
    }
  };

  const fetchTop1PercentTips = async (careerId: number) => {
    try {
      const career = careers.find(c => c.id === careerId);
      if (career) {
        // Generate some top 1% tips based on the career
        const tips = [
          `Master advanced concepts in ${career.name} - go beyond the basics`,
          `Build a strong professional network in the ${career.name} field`,
          `Contribute to open-source projects or real-world initiatives`,
          `Pursue relevant certifications and continuous learning`,
          `Develop leadership and communication skills`,
          `Stay updated with industry trends and innovations`,
          `Mentor others and share your knowledge`
        ];
        setTop1PercentTips(tips);
      }
    } catch (error) {
      console.error('Error fetching top 1% tips:', error);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const fetchCareerInsight = async (careerId: number) => {
    try {
      setLoadingCareerInsight(true);
      const response = await api.get<CareerInsight>(`/api/career-insight/${careerId}`);
      if (response.data) {
        setSelectedCareerInsight(response.data);
        console.log('✅ Career Insight loaded:', response.data);
      }
    } catch (error) {
      console.error('❌ Error fetching career insight:', error);
      toast({
        title: 'Error',
        description: 'Failed to load career insights',
        variant: 'destructive'
      });
    } finally {
      setLoadingCareerInsight(false);
    }
  };

  const fetchFullCareerDetails = async (careerId: number) => {
    try {
      console.log('🔍 Fetching full career details for ID:', careerId);
      setLoadingCareerDetailsState(true);
      const response = await api.get<Career>(`/api/career/${careerId}/details`);
      if (response.data) {
        console.log('✅ Full career details loaded:', response.data);
        setSelectedCareerForDialog(response.data);
      } else if (response.error) {
        console.error('❌ API Error:', response.error);
        toast({
          title: 'Error loading career details',
          description: response.error,
          variant: 'destructive'
        });
      }
    } catch (error) {
      console.error('❌ Error fetching full career details:', error);
      toast({
        title: 'Error',
        description: 'Failed to load career details',
        variant: 'destructive'
      });
    } finally {
      setLoadingCareerDetailsState(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1: return !!classLevel;
      case 2: return !!stream;
      case 3: return !!selectedDegreeId;
      case 4: return !!selectedBranchId;
      case 5: return !!selectedCareerId;
      case 6: return top1PercentTips.length > 0;
      default: return false;
    }
  };

  const handleGenerate = async () => {
    console.log('🔍 Checking selections on step', currentStep, ':', {
      selectedDegreeId,
      selectedBranchId,
      selectedCareerId,
      classLevel,
      stream,
      currentStep
    });

    // Make sure we have all required selections
    if (!classLevel) {
      toast({
        title: 'Missing class level',
        description: 'Please go back and select your class level',
        variant: 'destructive'
      });
      return;
    }

    if (!stream) {
      toast({
        title: 'Missing stream',
        description: 'Please go back and select your stream',
        variant: 'destructive'
      });
      return;
    }

    if (!selectedDegreeId) {
      toast({
        title: 'Missing degree',
        description: 'Please go back and select your degree',
        variant: 'destructive'
      });
      return;
    }

    if (!selectedBranchId) {
      toast({
        title: 'Missing branch',
        description: 'Please go back and select your branch/specialization',
        variant: 'destructive'
      });
      return;
    }

    if (!selectedCareerId) {
      toast({
        title: 'Missing career selection',
        description: 'Please go back and select a career',
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

    console.log('📤 Sending roadmap generate request:', request);
    const response = await api.post<ForwardRoadmapResponse>('/api/roadmap/generate', request);

    if (response.data) {
      console.log('✅ Roadmap generated:', response.data);
      setRoadmapId(response.data.roadmap_id);
      // Set default name
      const career = careers.find(c => c.id === selectedCareerId);
      setRoadmapName(`Forward: ${career?.name || 'My Career Path'}`);
      // Show save dialog instead of navigating immediately
      setShowSaveDialog(true);
      toast({
        title: 'Roadmap Generated!',
        description: 'Save your roadmap to your profile'
      });
    } else {
      console.error('❌ Generation failed:', response.error);
      toast({
        title: 'Generation failed',
        description: response.error || 'Could not generate roadmap',
        variant: 'destructive'
      });
    }
    setIsGenerating(false);
  };

  const handleSaveRoadmap = async () => {
    if (!roadmapId || !roadmapName.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a name for your roadmap',
        variant: 'destructive'
      });
      return;
    }

    setIsSavingRoadmap(true);
    try {
      const selectedCareer = careers.find(c => c.id === selectedCareerId);
      const selectedDegree = degrees.find(d => d.id === selectedDegreeId);
      const selectedBranch = branches.find(b => b.id === selectedBranchId);

      const saveRequest = {
        name: roadmapName,
        type: 'forward',
        career_goal: selectedCareer?.name || 'Career Goal',
        roadmap_data: {
          // Basic Info
          class_level: classLevel,
          stream: stream,

          // Degree Details
          degree_id: selectedDegreeId,
          degree_name: selectedDegree?.name || 'Unknown Degree',
          degree_duration: selectedDegree?.duration_years,
          degree_eligibility: selectedDegree?.eligibility,
          degree_description: selectedDegree?.short_description,

          // Branch/Specialization Details
          branch_id: selectedBranchId,
          branch_name: selectedBranch?.name || 'Unknown Branch',

          // Career Details
          career_id: selectedCareerId,
          career_name: selectedCareer?.name || 'Unknown Career',
          career_description: selectedCareer?.description,
          career_market_trend: selectedCareer?.market_trend,
          career_salary_range: selectedCareer?.salary_range,

          // Career Insights (Top 1% Details)
          career_insights: selectedCareerInsight ? {
            top_salary: selectedCareerInsight.top_salary,
            skills: selectedCareerInsight.skills,
            programs: selectedCareerInsight.programs,
            internships: selectedCareerInsight.internships,
            projects: selectedCareerInsight.projects
          } : null
        }
      };

      console.log('📤 Sending save request:', saveRequest);
      const response = await api.post<{ message: string; roadmap_id: number }>('/api/roadmap/save', saveRequest);
      console.log('📥 Save response:', response);

      if (response.data && response.data.roadmap_id) {
        toast({
          title: 'Success!',
          description: 'Roadmap saved to your profile'
        });
        // Close dialog and navigate to the newly saved roadmap
        setShowSaveDialog(false);
        const savedRoadmapId = response.data.roadmap_id;
        console.log('🔗 Navigating to saved roadmap ID:', savedRoadmapId);
        setTimeout(() => {
          navigate(`/roadmap/view/${savedRoadmapId}`);
        }, 500);
      } else {
        console.error('❌ Save error:', response.error);
        toast({
          title: 'Save failed',
          description: response.error || 'Could not save roadmap',
          variant: 'destructive'
        });
      }
    } catch (error) {
      console.error('❌ Exception saving roadmap:', error);
      toast({
        title: 'Error',
        description: 'Failed to save roadmap',
        variant: 'destructive'
      });
    } finally {
      setIsSavingRoadmap(false);
    }
  };

  const handleSkipSave = async () => {
    setShowSaveDialog(false);
    if (roadmapId) {
      navigate(`/roadmap/view/${roadmapId}`);
    }
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
          <div className="space-y-3 max-h-[500px] overflow-y-auto">
            {careers.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No careers found for this branch</p>
            ) : (
              careers.map((career) => {
                const isSelected = selectedCareerId === career.id;

                return (
                  <div
                    key={career.id}
                    onClick={() => {
                      setSelectedCareerId(career.id);
                      setSelectedCareerForDialog(career); // Set immediately for UI
                      setSelectedCareerInsight(null); // Reset previous insight
                      setShowTop1PercentDetails(false); // Reset to basic view
                      setShowCareerDialog(true);
                      // Fetch full details in background
                      fetchFullCareerDetails(career.id);
                    }}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${isSelected
                        ? 'border-primary bg-primary/5 shadow-sm'
                        : 'hover:bg-muted hover:border-muted-foreground/20'
                      }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        <div className={`h-5 w-5 rounded-full border-2 flex items-center justify-center ${isSelected ? 'border-primary bg-primary' : 'border-muted-foreground'
                          }`}>
                          {isSelected && <CheckCircle2 className="h-3 w-3 text-primary-foreground" />}
                        </div>
                      </div>

                      <div className="flex-1">
                        <div className="font-medium text-lg">{career.name}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                          Click to view details
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
              <div className="flex gap-3">
                <Star className="h-6 w-6 text-amber-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold text-amber-900">Become a Top 1% Professional</h3>
                  <p className="text-sm text-amber-800 mt-1">
                    {selectedCareerForDialog?.name && `Tips to excel as a ${selectedCareerForDialog.name} and join the top 1% in this field.`}
                  </p>
                </div>
              </div>
            </div>

            {top1PercentTips.length > 0 ? (
              <div className="space-y-3">
                {top1PercentTips.map((tip, index) => (
                  <div key={index} className="flex gap-3 p-4 bg-muted rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary text-primary-foreground text-sm font-medium">
                        {index + 1}
                      </div>
                    </div>
                    <p className="flex-1 text-sm leading-relaxed">{tip}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Select a career first to see top 1% tips</p>
              </div>
            )}
          </div>
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
            <span className="text-xl font-bold">AI Career Pilot</span>
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
                className={`flex items-center gap-1 text-sm ${step.id === currentStep
                    ? 'text-primary font-medium'
                    : step.id < currentStep
                      ? 'text-green-600'
                      : 'text-muted-foreground'
                  }`}
              >
                {step.id < currentStep ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <span className={`h-5 w-5 rounded-full flex items-center justify-center text-xs ${step.id === currentStep ? 'bg-primary text-primary-foreground' : 'bg-muted'
                    }`}>
                    {step.id}
                  </span>
                )}
                <span className="hidden sm:inline">{step.title}</span>
              </div>
            ))}
          </div>
          <Progress value={(currentStep / 6) * 100} className="h-2" />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{steps[currentStep - 1].title}</CardTitle>
            <CardDescription>
              {currentStep === 1 && 'What is your current education level?'}
              {currentStep === 2 && 'Which stream are you interested in?'}
              {currentStep === 3 && 'Select your preferred degree'}
              {currentStep === 4 && 'Choose your specialization'}
              {currentStep === 5 && 'Select your target career (click to see details)'}
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

              {currentStep < 6 ? (
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

        {/* Career Details Dialog */}
        <Dialog open={showCareerDialog} onOpenChange={(open) => {
          setShowCareerDialog(open);
          if (!open) setShowTop1PercentDetails(false);
        }}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader className="flex items-start justify-between pr-8">
              <div className="flex-1">
                <DialogTitle className="text-2xl">{selectedCareerForDialog?.name}</DialogTitle>
                <DialogDescription>
                  {showTop1PercentDetails ? 'Top 1% Career Path' : 'Career Overview'}
                </DialogDescription>
              </div>
            </DialogHeader>

            {selectedCareerForDialog && (
              <div className="space-y-6">
                {/* BASIC CAREER INFO - ALWAYS SHOW */}
                {!showTop1PercentDetails && (
                  <>
                    {loadingCareerDetails && (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                      </div>
                    )}

                    {!loadingCareerDetails && (
                      <>
                        {/* Description */}
                        {selectedCareerForDialog.description && (
                          <div>
                            <h3 className="font-semibold text-sm mb-2">About this Career</h3>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                              {selectedCareerForDialog.description}
                            </p>
                          </div>
                        )}

                        {/* Market Trend */}
                        {selectedCareerForDialog.market_trend && (
                          <div className="flex gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
                            <TrendingUp className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="text-sm font-medium text-green-900">Market Trend</p>
                              <p className="text-sm text-green-800">{selectedCareerForDialog.market_trend}</p>
                            </div>
                          </div>
                        )}

                        {/* Salary Range */}
                        {selectedCareerForDialog.salary_range && (
                          <div className="flex gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <DollarSign className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="text-sm font-medium text-blue-900">Salary Range</p>
                              <p className="text-sm text-blue-800 font-semibold">{selectedCareerForDialog.salary_range}</p>
                            </div>
                          </div>
                        )}

                        {/* View Top 1% Button */}
                        <Button
                          onClick={() => {
                            setShowTop1PercentDetails(true);
                            if (!selectedCareerInsight && selectedCareerForDialog.id) {
                              fetchCareerInsight(selectedCareerForDialog.id);
                            }
                          }}
                          className="w-full"
                          size="lg"
                          variant="default"
                        >
                          <Star className="h-4 w-4 mr-2" />
                          View Top 1% Details
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </Button>

                        {/* Skip Button */}
                        <Button
                          onClick={() => {
                            setShowCareerDialog(false);
                            handleNext();
                          }}
                          className="w-full"
                          variant="outline"
                        >
                          Skip to Top 1% Tips
                        </Button>
                      </>
                    )}
                  </>
                )}

                {/* TOP 1% DETAILS - SHOW WHEN CLICKED */}
                {showTop1PercentDetails && (
                  <>
                    {/* Loading State */}
                    {loadingCareerInsight && (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                      </div>
                    )}

                    {!loadingCareerInsight && selectedCareerInsight && (
                      <>
                        {/* Top Salary */}
                        {selectedCareerInsight.top_salary && (
                          <div className="flex gap-3 p-4 bg-amber-50 rounded-lg border border-amber-200">
                            <Star className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="text-sm font-medium text-amber-900">Top 1% Salary</p>
                              <p className="text-sm text-amber-800 font-semibold text-lg">{selectedCareerInsight.top_salary}</p>
                            </div>
                          </div>
                        )}

                        {/* Skills */}
                        {selectedCareerInsight.skills && selectedCareerInsight.skills.length > 0 && (
                          <div>
                            <h3 className="font-semibold text-sm mb-3">Top 1% Skills Required</h3>
                            <div className="flex flex-wrap gap-2">
                              {selectedCareerInsight.skills.map((skill, idx) => (
                                <span key={idx} className="px-3 py-1.5 bg-primary/10 text-primary text-xs rounded-full font-medium">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Programs */}
                        {selectedCareerInsight.programs && selectedCareerInsight.programs.length > 0 && (
                          <div>
                            <h3 className="font-semibold text-sm mb-3">Recommended Learning Programs</h3>
                            <div className="space-y-2">
                              {selectedCareerInsight.programs.map((program, idx) => (
                                <div key={idx} className="flex items-center gap-2 p-2 bg-muted rounded">
                                  <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0" />
                                  <span className="text-sm">{program}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Top Internships */}
                        {selectedCareerInsight.internships && selectedCareerInsight.internships.length > 0 && (
                          <div>
                            <h3 className="font-semibold text-sm mb-3">Top 1% Internship Companies</h3>
                            <div className="space-y-2">
                              {selectedCareerInsight.internships.map((internship, idx) => (
                                <div key={idx} className="flex items-center gap-2 p-2 bg-amber-50 rounded border border-amber-200">
                                  <Star className="h-4 w-4 text-amber-600 flex-shrink-0" />
                                  <span className="text-sm font-medium">{internship}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Projects */}
                        {selectedCareerInsight.projects && (
                          <div>
                            <h3 className="font-semibold text-sm mb-3">Top 1% Projects to Build</h3>
                            <div className="space-y-3">
                              {selectedCareerInsight.projects.production && selectedCareerInsight.projects.production.length > 0 && (
                                <div>
                                  <p className="text-xs font-semibold text-muted-foreground mb-2">Production Projects</p>
                                  <ul className="space-y-1.5">
                                    {selectedCareerInsight.projects.production.map((proj, idx) => (
                                      <li key={idx} className="text-sm flex items-center gap-2 p-2 bg-muted rounded">
                                        <span className="w-2 h-2 bg-primary rounded-full" />
                                        {proj}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {selectedCareerInsight.projects.research && selectedCareerInsight.projects.research.length > 0 && (
                                <div>
                                  <p className="text-xs font-semibold text-muted-foreground mb-2">Research Projects</p>
                                  <ul className="space-y-1.5">
                                    {selectedCareerInsight.projects.research.map((proj, idx) => (
                                      <li key={idx} className="text-sm flex items-center gap-2 p-2 bg-muted rounded">
                                        <span className="w-2 h-2 bg-blue-600 rounded-full" />
                                        {proj}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Continue Button */}
                        <Button
                          onClick={() => {
                            setShowCareerDialog(false);
                            handleNext();
                          }}
                          className="w-full"
                          size="lg"
                        >
                          <Sparkles className="h-4 w-4 mr-2" />
                          Continue to Top 1% Tips
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </Button>

                        {/* Back Button */}
                        <Button
                          onClick={() => setShowTop1PercentDetails(false)}
                          className="w-full"
                          variant="outline"
                        >
                          <ArrowLeft className="h-4 w-4 mr-2" />
                          Back to Career Overview
                        </Button>
                      </>
                    )}
                  </>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Save Roadmap Dialog */}
        <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Save Your Roadmap</DialogTitle>
              <DialogDescription>
                Give your roadmap a name to save it to your profile
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Roadmap Name</label>
                <input
                  type="text"
                  value={roadmapName}
                  onChange={(e) => setRoadmapName(e.target.value)}
                  placeholder="e.g., AI/ML Engineer Path 2024"
                  className="w-full mt-2 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={handleSaveRoadmap}
                  disabled={isSavingRoadmap || !roadmapName.trim()}
                  className="flex-1"
                  size="lg"
                >
                  {isSavingRoadmap ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                      Save Roadmap
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleSkipSave}
                  variant="outline"
                  className="flex-1"
                  size="lg"
                >
                  Skip for Now
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
};

export default ForwardPlanner;
