import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile, switchDemoRole } from '../api/auth';

interface AuthContextType {
  user: UserProfile | null;
  role: 'PROCUREMENT_OFFICER' | 'STANDARDS_AUDITOR' | 'ADMIN';
  isLoading: boolean;
  switchRole: (role: 'PROCUREMENT_OFFICER' | 'STANDARDS_AUDITOR' | 'ADMIN') => Promise<void>;
  isModalOpen: boolean;
  setIsModalOpen: (open: boolean) => void;
}

const DEFAULT_OFFICER: UserProfile = {
  id: 1,
  username: 'officer_tender',
  full_name: 'Shri Rajesh Kumar',
  designation: 'Executive Engineer / Procurement Officer',
  department: 'National Thermal Power Corporation (NTPC)',
  role: 'PROCUREMENT_OFFICER',
  is_active: true,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('normvault_user');
    return saved ? JSON.parse(saved) : DEFAULT_OFFICER;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const role = user?.role || 'PROCUREMENT_OFFICER';

  const switchRoleHandler = async (newRole: 'PROCUREMENT_OFFICER' | 'STANDARDS_AUDITOR' | 'ADMIN') => {
    setIsLoading(true);
    try {
      const resp = await switchDemoRole(newRole);
      localStorage.setItem('normvault_token', resp.access_token);
      localStorage.setItem('normvault_user', JSON.stringify(resp.user));
      setUser(resp.user);
    } catch {
      // Fallback offline mock for dev/tests
      const mockUsers: Record<string, UserProfile> = {
        PROCUREMENT_OFFICER: {
          id: 1,
          username: 'officer_tender',
          full_name: 'Shri Rajesh Kumar',
          designation: 'Executive Engineer / Procurement Officer',
          department: 'National Thermal Power Corporation (NTPC)',
          role: 'PROCUREMENT_OFFICER',
          is_active: true,
        },
        STANDARDS_AUDITOR: {
          id: 2,
          username: 'auditor_bis',
          full_name: 'Dr. Ananya Sharma',
          designation: 'Scientist-D / Standards Reviewer',
          department: 'Bureau of Indian Standards (BIS)',
          role: 'STANDARDS_AUDITOR',
          is_active: true,
        },
        ADMIN: {
          id: 3,
          username: 'admin_cvc',
          full_name: 'Smt. Sunita Verma',
          designation: 'Chief Vigilance Officer & Administrator',
          department: 'Central Vigilance Commission (CVC)',
          role: 'ADMIN',
          is_active: true,
        },
      };
      const fallbackUser = mockUsers[newRole] || DEFAULT_OFFICER;
      setUser(fallbackUser);
      localStorage.setItem('normvault_user', JSON.stringify(fallbackUser));
    } finally {
      setIsLoading(false);
      setIsModalOpen(false);
    }
  };

  useEffect(() => {
    // If no token, switch to default role once
    if (!localStorage.getItem('normvault_token')) {
      switchRoleHandler('PROCUREMENT_OFFICER').catch(() => {});
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isLoading,
        switchRole: switchRoleHandler,
        isModalOpen,
        setIsModalOpen,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
