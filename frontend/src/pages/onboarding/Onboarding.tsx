import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, FlaskConical, Briefcase, Palette, MapPin, Languages, Loader2, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { indianStates } from '@/data/indianStates';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

// Match FastAPI ClassLevelUpdateRequest: class_level = "class_10" or "class_12"
type ClassLevel = 'class_10' | 'class_12';
// Match FastAPI StreamUpdateRequest: stream = "science" / "commerce" / "arts"
type Stream = 'science' | 'commerce' | 'arts';

interface OnboardingData {
  classLevel: ClassLevel | null;
  stream: Stream | null;
  state: string;
  language: string;
}

const Onboarding = () => {
  const navigate = useNavigate();
  const { updateUser } = useAuth();
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    classLevel: null,
    stream: null,
    state: '',
    language: '',
  });

  const totalSteps = data.classLevel === 'class_12' ? 4 : 3;

  const handleClassSelect = async (classLevel: ClassLevel) => {
  setData({ ...data, classLevel, stream: null });
  
  try {
    const response = await api.post('/api/profile/class-level', { 
      class_level: classLevel 
    });
    
    console.log('Class level API response:', response); // Debug log
    
    if (response.error) {
      console.error('Failed to save class level:', response.error);
      
    }
  } catch (error) {
    console.error('Error saving class level:', error);
    
  }

  if (classLevel === 'class_10') {
    setStep(2); 
  } else {
    setStep(2); 
  }
};


  const handleStreamSelect = async (stream: Stream) => {
    setData({ ...data, stream });
    
    // POST /api/profile/profile/stream with { stream: "science" / "commerce" / "arts" }
    try {
      await api.post('/api/profile/profile/stream', { stream });
    } catch (error) {
      console.error('Failed to update stream:', error);
    }

    setStep(3);
  };

  const handleStateSelect = (state: string) => {
    setData({ ...data, state });
  };

  const handleLanguageSelect = (language: string) => {
    setData({ ...data, language });
  };

  const handleComplete = async () => {
    if (!data.state || !data.language) {
      toast({
        title: 'Please complete all fields',
        description: 'Select your state and preferred language.',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // PUT /api/profile/profile to update location and language
      const response = await api.put('/api/profile/profile', {
        location: data.state,
        language: data.language,
      });

      if (response.error) {
        throw new Error(response.error);
      }

      // Update local user state
      updateUser({
        isOnboarded: true,
      });

      // Show success and navigate
      setStep(totalSteps + 1); // Success step
      
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 2000);

    } catch (error) {
      toast({
        title: 'Failed to save preferences',
        description: error instanceof Error ? error.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderProgress = () => (
    <div className="mb-8 flex items-center justify-center gap-2">
      {Array.from({ length: totalSteps }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'h-2 w-12 rounded-full transition-colors',
            i + 1 <= step ? 'bg-primary' : 'bg-muted'
          )}
        />
      ))}
    </div>
  );

  // Step 1: Class Selection
  if (step === 1) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-lg">
          {renderProgress()}
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">What class are you in?</CardTitle>
              <CardDescription>This helps us personalize your learning experience</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <Button
                variant="outline"
                className="h-24 flex-col gap-2 text-lg"
                onClick={() => handleClassSelect('class_10')}
              >
                <GraduationCap className="h-8 w-8" />
                10th Class
              </Button>
              <Button
                variant="outline"
                className="h-24 flex-col gap-2 text-lg"
                onClick={() => handleClassSelect('class_12')}
              >
                <GraduationCap className="h-8 w-8" />
                12th Class
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Step 2: Stream Selection (only for 12th)
  if (step === 2 && data.classLevel === 'class_12') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-lg">
          {renderProgress()}
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Choose your stream</CardTitle>
              <CardDescription>Select your academic stream</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <Button
                variant="outline"
                className="h-20 justify-start gap-4 px-6 text-lg"
                onClick={() => handleStreamSelect('science')}
              >
                <FlaskConical className="h-6 w-6 text-blue-500" />
                <div className="text-left">
                  <div>Science</div>
                  <div className="text-sm text-muted-foreground">Physics, Chemistry, Biology/Math</div>
                </div>
              </Button>
              <Button
                variant="outline"
                className="h-20 justify-start gap-4 px-6 text-lg"
                onClick={() => handleStreamSelect('commerce')}
              >
                <Briefcase className="h-6 w-6 text-green-500" />
                <div className="text-left">
                  <div>Commerce</div>
                  <div className="text-sm text-muted-foreground">Accounts, Economics, Business</div>
                </div>
              </Button>
              <Button
                variant="outline"
                className="h-20 justify-start gap-4 px-6 text-lg"
                onClick={() => handleStreamSelect('arts')}
              >
                <Palette className="h-6 w-6 text-purple-500" />
                <div className="text-left">
                  <div>Arts / Humanities</div>
                  <div className="text-sm text-muted-foreground">History, Geography, Political Science</div>
                </div>
              </Button>
            </CardContent>
          </Card>
          <div className="mt-4 text-center">
            <Button variant="ghost" onClick={() => setStep(1)}>
              Back
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Step 2/3: Location & Language
  const locationStep = data.classLevel === 'class_12' ? 3 : 2;
  if (step === locationStep || (step === 2 && data.classLevel === 'class_10')) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-lg">
          {renderProgress()}
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Where are you from?</CardTitle>
              <CardDescription>This helps us show relevant content for your state board</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium">
                  <MapPin className="h-4 w-4" />
                  State
                </label>
                <Select value={data.state} onValueChange={handleStateSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your state" />
                  </SelectTrigger>
                  <SelectContent>
                    {indianStates.map((state) => (
                      <SelectItem key={state.value} value={state.value}>
                        {state.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium">
                  <Languages className="h-4 w-4" />
                  Preferred Language
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <Button
                    type="button"
                    variant={data.language === 'english' ? 'default' : 'outline'}
                    className="h-14"
                    onClick={() => handleLanguageSelect('english')}
                  >
                    English
                  </Button>
                  <Button
                    type="button"
                    variant={data.language === 'hindi' ? 'default' : 'outline'}
                    className="h-14"
                    onClick={() => handleLanguageSelect('hindi')}
                  >
                    हिंदी
                  </Button>
                </div>
              </div>

              <Button 
                className="w-full" 
                onClick={handleComplete}
                disabled={!data.state || !data.language || isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Complete Setup'
                )}
              </Button>
            </CardContent>
          </Card>
          <div className="mt-4 text-center">
            <Button variant="ghost" onClick={() => setStep(step - 1)}>
              Back
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Success Step
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md text-center">
        <CardContent className="pt-10">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-100">
            <CheckCircle2 className="h-10 w-10 text-green-600" />
          </div>
          <CardTitle className="mb-2 text-2xl">You're all set!</CardTitle>
          <CardDescription className="text-base">
            Redirecting you to your personalized dashboard...
          </CardDescription>
          <div className="mt-6">
            <Loader2 className="mx-auto h-6 w-6 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Onboarding;