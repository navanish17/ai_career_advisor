import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Loader2, Bell, Mail } from 'lucide-react';
import { ALERT_TYPES, type AlertType } from '@/types/college';

interface AlertSetupFormProps {
  defaultEmail?: string;
  onSubmit: (email: string, alertTypes: AlertType[]) => Promise<void>;
  isLoading?: boolean;
}

export const AlertSetupForm = ({
  defaultEmail = '',
  onSubmit,
  isLoading = false,
}: AlertSetupFormProps) => {
  const [email, setEmail] = useState(defaultEmail);
  const [selectedTypes, setSelectedTypes] = useState<AlertType[]>([
    'registration_start',
    'registration_3days',
    'registration_last',
    'exam_1day',
  ]);
  const [emailError, setEmailError] = useState('');

  const handleToggleType = (type: AlertType) => {
    setSelectedTypes((prev) =>
      prev.includes(type)
        ? prev.filter((t) => t !== type)
        : [...prev, type]
    );
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async () => {
    if (!email.trim()) {
      setEmailError('Email is required');
      return;
    }
    if (!validateEmail(email)) {
      setEmailError('Please enter a valid email');
      return;
    }
    if (selectedTypes.length === 0) {
      return;
    }
    setEmailError('');
    await onSubmit(email, selectedTypes);
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="alert-email" className="flex items-center gap-2">
          <Mail className="h-4 w-4" />
          Email Address
        </Label>
        <Input
          id="alert-email"
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (emailError) setEmailError('');
          }}
          className={emailError ? 'border-destructive' : ''}
        />
        {emailError && (
          <p className="text-sm text-destructive">{emailError}</p>
        )}
      </div>

      <div className="space-y-3">
        <Label className="flex items-center gap-2">
          <Bell className="h-4 w-4" />
          Alert Types
        </Label>
        <div className="space-y-2">
          {ALERT_TYPES.map((type) => (
            <div key={type.value} className="flex items-center space-x-2">
              <Checkbox
                id={type.value}
                checked={selectedTypes.includes(type.value)}
                onCheckedChange={() => handleToggleType(type.value)}
              />
              <Label
                htmlFor={type.value}
                className="text-sm font-normal cursor-pointer"
              >
                {type.label}
              </Label>
            </div>
          ))}
        </div>
      </div>

      <Button
        onClick={handleSubmit}
        disabled={isLoading || selectedTypes.length === 0}
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Setting Alerts...
          </>
        ) : (
          <>
            <Bell className="h-4 w-4 mr-2" />
            Set Alerts ({selectedTypes.length})
          </>
        )}
      </Button>
    </div>
  );
};

export default AlertSetupForm;
