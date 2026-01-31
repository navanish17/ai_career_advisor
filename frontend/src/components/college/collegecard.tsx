import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Star, MapPin, Building2, Trophy, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import type { CollegeBasic, CollegeDetail } from '@/types/college';

interface CollegeCardProps {
  college: CollegeBasic | CollegeDetail;
  isTopCollege?: boolean;
  isLoadingDetails?: boolean;
  onGetDetails?: () => void;
  onSetAlert?: () => void;
  onViewDetails?: () => void;
}

const isCollegeDetail = (college: CollegeBasic | CollegeDetail): college is CollegeDetail => {
  return 'entrance_exam' in college || 'fees' in college || 'avg_package' in college;
};

export const CollegeCard = ({
  college,
  isTopCollege = false,
  isLoadingDetails = false,
  onGetDetails,
  onSetAlert,
  onViewDetails,
}: CollegeCardProps) => {
  const [isExpanded, setIsExpanded] = useState(isTopCollege);
  const hasDetails = isCollegeDetail(college);

  // Status logic
  const isChecking = college.status === 'checking' || college.status === 'pending_check';
  const isChecked = college.status === 'checked';
  const offersProgram = college.offers_program === true;
  const isNotOffering = isChecked && !offersProgram;

  return (
    <Card className={`transition-all ${isTopCollege ? 'border-primary shadow-md' : 'hover:shadow-md'} ${isNotOffering ? 'opacity-60 bg-muted/20' : ''}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2">
            {isTopCollege && (
              <Star className="h-5 w-5 text-yellow-500 fill-yellow-500 mt-0.5 flex-shrink-0" />
            )}
            <div>
              <CardTitle className="text-lg leading-tight">{college.name}</CardTitle>
              <div className="flex flex-wrap items-center gap-2 mt-1 text-sm text-muted-foreground">
                {college.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5" />
                    {college.location}
                  </span>
                )}
                {college.established && (
                  <span className="flex items-center gap-1">
                    <Building2 className="h-3.5 w-3.5" />
                    Est. {college.established}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-end gap-1">
            {college.nirf_rank && (
              <Badge variant="secondary" className="flex-shrink-0">
                <Trophy className="h-3 w-3 mr-1" />
                #{college.nirf_rank} NIRF
              </Badge>
            )}

            {/* Availability Status Badges */}
            {isChecking && (
              <Badge variant="outline" className="flex-shrink-0 text-muted-foreground">
                <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                Checking...
              </Badge>
            )}
            {isChecked && offersProgram && (
              <Badge className="bg-green-600 hover:bg-green-700 flex-shrink-0">
                Available
              </Badge>
            )}
            {isChecked && !offersProgram && (
              <Badge variant="destructive" className="flex-shrink-0">
                Not Offered
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-2">
        {/* Show details if available and expanded */}
        {hasDetails && isExpanded && (
          <div className="space-y-3 mb-4 pt-2 border-t">
            <div className="grid grid-cols-2 gap-3 text-sm">
              {(college as CollegeDetail).entrance_exam && (
                <div>
                  <p className="text-muted-foreground">Entrance Exam</p>
                  <p className="font-medium">{(college as CollegeDetail).entrance_exam}</p>
                </div>
              )}
              {(college as CollegeDetail).fees && (
                <div>
                  <p className="text-muted-foreground">Fees</p>
                  <p className="font-medium">{(college as CollegeDetail).fees}</p>
                </div>
              )}
              {(college as CollegeDetail).seats && (
                <div>
                  <p className="text-muted-foreground">Total Seats</p>
                  <p className="font-medium">{(college as CollegeDetail).seats}</p>
                </div>
              )}
              {(college as CollegeDetail).duration && (
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">{(college as CollegeDetail).duration}</p>
                </div>
              )}
              {(college as CollegeDetail).avg_package && (
                <div>
                  <p className="text-muted-foreground">Avg Package</p>
                  <p className="font-medium">{(college as CollegeDetail).avg_package}</p>
                </div>
              )}
              {(college as CollegeDetail).cutoff && (
                <div>
                  <p className="text-muted-foreground">Cutoff</p>
                  <p className="font-medium">{(college as CollegeDetail).cutoff}</p>
                </div>
              )}
            </div>

            {(college as CollegeDetail).top_recruiters && (college as CollegeDetail).top_recruiters!.length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">Top Recruiters</p>
                <div className="flex flex-wrap gap-1">
                  {(college as CollegeDetail).top_recruiters!.slice(0, 5).map((recruiter, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {recruiter}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Loading skeleton for details */}
        {isLoadingDetails && (
          <div className="space-y-3 mb-4 pt-2 border-t">
            <div className="grid grid-cols-2 gap-3">
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-2">
          {hasDetails ? (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="h-4 w-4 mr-1" />
                    Hide Details
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 mr-1" />
                    Show Details
                  </>
                )}
              </Button>
              {onViewDetails && (
                <Button variant="outline" size="sm" onClick={onViewDetails}>
                  View Full Details
                </Button>
              )}
              {onSetAlert && (
                <Button size="sm" onClick={onSetAlert}>
                  🔔 Set Alert
                </Button>
              )}
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={onGetDetails}
              disabled={isLoadingDetails || isChecking || isNotOffering}
            >
              {isLoadingDetails ? (
                <>
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  Loading...
                </>
              ) : isChecking ? (
                'Checking...'
              ) : isNotOffering ? (
                'Not Offered'
              ) : (
                'Get Details'
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default CollegeCard;
