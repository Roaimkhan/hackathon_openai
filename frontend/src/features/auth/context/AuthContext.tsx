import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { PropsWithChildren } from "react";
import { authStorage } from "../../../lib/storage";
import { ApiError } from "../../../services/api";
import { authService } from "../../../services/authService";
import type { LoginPayload, Profile, RegisterPayload, TasteProfile, User } from "../../../services/types";

interface AuthContextValue {
  user: User | null;
  profile: Profile | null;
  tasteProfile: TasteProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(authStorage.getUser());
  const [profile] = useState<Profile | null>(null);
  const [tasteProfile] = useState<TasteProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function restoreSession(): Promise<void> {
      if (!authStorage.getToken()) {
        if (active) setIsLoading(false);
        return;
      }
      try {
        const currentUser = await authService.currentUser();
        if (active) {
          setUser(currentUser);
          authStorage.setUser(currentUser);
        }
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) authStorage.clear();
        if (active) setUser(null);
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void restoreSession();
    return () => { active = false; };
  }, []);

  const applySession = useCallback((session: { access_token: string; user: User }) => {
    authStorage.setToken(session.access_token);
    authStorage.setUser(session.user);
    setUser(session.user);
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    applySession(await authService.login(payload));
  }, [applySession]);

  const register = useCallback(async (payload: RegisterPayload) => {
    applySession(await authService.register(payload));
  }, [applySession]);

  const logout = useCallback(() => {
    authStorage.clear();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user, profile, tasteProfile, isAuthenticated: user !== null, isLoading, login, register, logout,
  }), [user, profile, tasteProfile, isLoading, login, register, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
