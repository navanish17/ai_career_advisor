import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Search, GraduationCap, Loader2, Bell, Building } from 'lucide-react';
import { indianStates } from '@/data/indianStates';
import { CollegeCard } from '@/components/college/collegecard';
import { CollegeDetailDialog } from '@/components/college/collegedetail';
import type { Degree, Branch } from '@/types/career';
import type {
  CollegeFinderResponse,
  CollegeBasic,
  CollegeDetail,
  AlertType,
} from '@/types/college';

const CollegeFinder = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  // Filter states
  const [selectedState, setSelectedState] = useState('');
  const [selectedDegree, setSelectedDegree] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [selectedDegreeId, setSelectedDegreeId] = useState<number | null>(null);

  // Data states
  const [degrees, setDegrees] = useState<Degree[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [searchResults, setSearchResults] = useState<CollegeFinderResponse | null>(null);
  const [collegeDetails, setCollegeDetails] = useState<Map<number, CollegeDetail>>(new Map());

  // Loading states
  const [isLoadingDegrees, setIsLoadingDegrees] = useState(true);
  const [isLoadingBranches, setIsLoadingBranches] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [loadingCollegeId, setLoadingCollegeId] = useState<number | null>(null);
  const [isSettingAlert, setIsSettingAlert] = useState(false);

  // Dialog state
  const [selectedCollege, setSelectedCollege] = useState<CollegeDetail | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Fetch degrees on mount
  useEffect(() => {
    const fetchDegrees = async () => {
      const res = await api.get<Degree[]>('/api/degree/all');
      if (res.data) {
        setDegrees(res.data);
      }
      setIsLoadingDegrees(false);
    };
    fetchDegrees();
  }, []);

  // Fetch branches when degree changes
  useEffect(() => {
    if (!selectedDegreeId) {
      setBranches([]);
      setSelectedBranch('');
      return;
    }

    const fetchBranches = async () => {
      setIsLoadingBranches(true);
      const res = await api.get<Branch[]>(`/api/branch/from-degree/${selectedDegreeId}`);
      if (res.data) {
        setBranches(res.data);
      }
      setIsLoadingBranches(false);
    };
    fetchBranches();
  }, [selectedDegreeId]);

  const handleDegreeChange = (degreeName: string) => {
    setSelectedDegree(degreeName);
    setSelectedBranch('');
    const degree = degrees.find((d) => d.name === degreeName);
    setSelectedDegreeId(degree?.id ?? null);
  };

  const handleSearch = async () => {
    if (!selectedState || !selectedDegree || !selectedBranch) {
      toast({
        title: 'Missing Filters',
        description: 'Please select state, degree, and branch to search.',
        variant: 'destructive',
      });
      return;
    }

    setIsSearching(true);
    setSearchResults(null);
    setCollegeDetails(new Map());

    const stateLabel = indianStates.find((s) => s.value === selectedState)?.label || selectedState;

    const res = await api.post<CollegeFinderResponse>('/api/colleges/finder', {
      state: stateLabel,
      degree: selectedDegree,
      branch: selectedBranch,
    });

    if (res.data) {
      console.log('📡 Search Results:', res.data);
      setSearchResults(res.data);

      // Trigger background checks
      checkAvailability(res.data.colleges, selectedDegree, selectedBranch);
    } else if (res.error) {
      toast({
        title: 'Search Failed',
        description: res.error || 'Could not find colleges. Please try again.',
        variant: 'destructive',
      });
    }
    setIsSearching(false);
  };

  // Background availability checker
  const checkAvailability = async (colleges: CollegeBasic[], degree: string, branch: string) => {
    console.log('🔄 Starting background availability checks...');

    for (const college of colleges) {
      try {
        // Update status to checking
        updateCollegeStatus(college.id, { status: 'checking' });

        const res = await api.post<{ offers_program: boolean }>('/api/colleges/check-availability', {
          college_id: college.id,
          degree,
          branch,
        });

        if (res.data) {
          updateCollegeStatus(college.id, {
            status: 'checked',
            offers_program: res.data.offers_program
          });
        }
      } catch (error) {
        console.error(`❌ Failed to check ${college.name}`, error);
        updateCollegeStatus(college.id, { status: 'check_failed' });
      }
    }
    console.log('✅ All checks completed');
  };

  const updateCollegeStatus = (id: number, updates: Partial<CollegeBasic>) => {
    setSearchResults((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        colleges: prev.colleges.map((c) =>
          c.id === id ? { ...c, ...updates } : c
        ),
      };
    });
  };

  const handleGetDetails = async (college: CollegeBasic) => {
    setLoadingCollegeId(college.id);

    const res = await api.post<CollegeDetail>('/api/colleges/details', {
      college_id: college.id,
      degree: selectedDegree,
      branch: selectedBranch,
    });

    if (res.data) {
      setCollegeDetails((prev) => new Map(prev).set(college.id, res.data));
    } else if (res.error) {
      toast({
        title: 'Failed to Load Details',
        description: res.error || 'Could not load college details.',
        variant: 'destructive',
      });
    }
    setLoadingCollegeId(null);
  };

  const handleOpenDialog = (college: CollegeDetail) => {
    setSelectedCollege(college);
    setIsDialogOpen(true);
  };

  const handleSetAlert = async (email: string, alertTypes: AlertType[]) => {
    if (!selectedCollege) return;

    setIsSettingAlert(true);
    const res = await api.post('/api/admission-alerts/set-alert', {
      user_email: email,
      college_name: selectedCollege.name,
      degree: selectedDegree,
      branch: selectedBranch,
      alert_types: alertTypes,
    });

    if (res.data) {
      toast({
        title: 'Alerts Set Successfully!',
        description: `You'll receive ${alertTypes.length} alerts for ${selectedCollege.name}`,
      });
      setIsDialogOpen(false);
    } else if (res.error) {
      toast({
        title: 'Failed to Set Alerts',
        description: res.error || 'Could not set alerts. Please try again.',
        variant: 'destructive',
      });
    }
    setIsSettingAlert(false);
  };

  const totalColleges = searchResults?.total_colleges || 0;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center gap-4 px-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-2">
            <GraduationCap className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">College Finder</span>
          </div>
          <div className="ml-auto">
            <Button variant="outline" onClick={() => navigate('/my-alerts')}>
              <Bell className="h-4 w-4 mr-2" />
              My Alerts
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-5xl">
        {/* Search Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Search Filters
            </CardTitle>
            <CardDescription>
              Find colleges by state, degree, and branch
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <label className="text-sm font-medium">State</label>
                <Select value={selectedState} onValueChange={setSelectedState}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select State" />
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
                <label className="text-sm font-medium">Degree</label>
                {isLoadingDegrees ? (
                  <Skeleton className="h-10" />
                ) : (
                  <Select value={selectedDegree} onValueChange={handleDegreeChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Degree" />
                    </SelectTrigger>
                    <SelectContent>
                      {degrees.map((degree) => (
                        <SelectItem key={degree.id} value={degree.name}>
                          {degree.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Branch</label>
                {isLoadingBranches ? (
                  <Skeleton className="h-10" />
                ) : (
                  <Select
                    value={selectedBranch}
                    onValueChange={setSelectedBranch}
                    disabled={!selectedDegreeId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={selectedDegreeId ? 'Select Branch' : 'Select Degree first'} />
                    </SelectTrigger>
                    <SelectContent>
                      {branches.map((branch) => (
                        <SelectItem key={branch.id} value={branch.name}>
                          {branch.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>

            <Button
              onClick={handleSearch}
              disabled={isSearching || !selectedState || !selectedDegree || !selectedBranch}
              className="w-full sm:w-auto mt-4"
            >
              {isSearching ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Find Colleges
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Search Results */}
        {isSearching && (
          <div className="space-y-4">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-48" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
        )}

        {searchResults && !isSearching && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Building className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">
                Results ({totalColleges} college{totalColleges !== 1 ? 's' : ''} found)
              </h2>
            </div>

            {/* College List */}
            {searchResults.colleges.length > 0 ? (
              searchResults.colleges.map((college) => {
                const details = collegeDetails.get(college.id);
                return (
                  <CollegeCard
                    key={college.id}
                    college={details || college}
                    isLoadingDetails={loadingCollegeId === college.id}
                    onGetDetails={() => handleGetDetails(college)}
                    onSetAlert={details ? () => handleOpenDialog(details) : undefined}
                    onViewDetails={details ? () => handleOpenDialog(details) : undefined}
                  />
                );
              })
            ) : (
              <Card className="p-8 text-center">
                <Building className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  No colleges found for the selected criteria.
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  Try adjusting your filters.
                </p>
              </Card>
            )}
          </div>
        )}

        {/* College Detail Dialog */}
        <CollegeDetailDialog
          college={selectedCollege}
          degree={selectedDegree}
          branch={selectedBranch}
          userEmail={user?.email}
          isOpen={isDialogOpen}
          onClose={() => setIsDialogOpen(false)}
          onSetAlert={handleSetAlert}
          isSettingAlert={isSettingAlert}
        />
      </main>
    </div>
  );
};

export default CollegeFinder;
