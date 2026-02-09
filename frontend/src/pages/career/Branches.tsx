import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, GitBranch, Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import type { Branch } from '@/types/career';

const Branches = () => {
  const navigate = useNavigate();
  const { degreeId } = useParams<{ degreeId: string }>();

  const [branches, setBranches] = useState<Branch[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBranches = async () => {
      if (!degreeId) {
        navigate('/degrees');
        return;
      }

      setIsLoading(true);
      try {
        const response = await api.get(`/api/branch/from-degree/${degreeId}`);
        const branchData = response.data as Branch[] | undefined;
        setBranches(branchData || []);
      } catch (error: any) {
        setBranches([]); // Reset to empty array on error
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Failed to load branches',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchBranches();
  }, [degreeId, navigate]);

  const handleBranchClick = (branchId: number) => {
    navigate(`/careers/${branchId}`);
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-6 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/degrees')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Specializations</h1>
            <p className="text-muted-foreground">Choose your area of focus</p>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : branches.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <GitBranch className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No specializations found for this degree</p>
              <Button variant="link" onClick={() => navigate('/degrees')}>
                Browse other degrees
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {branches.map((branch) => (
              <Card
                key={branch.id}
                className="cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
                onClick={() => handleBranchClick(branch.id)}
              >
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <GitBranch className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{branch.name}</CardTitle>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Branches;
