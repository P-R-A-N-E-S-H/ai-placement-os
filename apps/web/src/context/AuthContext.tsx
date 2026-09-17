"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, authApi } from "@/lib/api/auth";
import { UserProfile, profileApi } from "@/lib/api/profile";

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (email: string, password: string, fullName: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Load session from browser storage on boot
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem("placement_os_access_token");
        const storedRefresh = localStorage.getItem("placement_os_refresh_token");

        if (storedToken && storedRefresh) {
          setToken(storedToken);
          setRefreshToken(storedRefresh);

          // Fetch current user
          const { data: userData, error } = await authApi.getMe(storedToken);
          if (userData) {
            setUser(userData);
            // Fetch profile
            const { data: profileData } = await profileApi.getProfile(storedToken);
            if (profileData) {
              setProfile(profileData);
            }
          } else {
            // Token might be expired, try refreshing
            const { data: refreshData } = await authApi.refreshToken(storedRefresh);
            if (refreshData) {
              setToken(refreshData.access_token);
              setRefreshToken(refreshData.refresh_token);
              setUser(refreshData.user);
              localStorage.setItem("placement_os_access_token", refreshData.access_token);
              localStorage.setItem("placement_os_refresh_token", refreshData.refresh_token);

              const { data: profileData } = await profileApi.getProfile(refreshData.access_token);
              if (profileData) setProfile(profileData);
            } else {
              localStorage.removeItem("placement_os_access_token");
              localStorage.removeItem("placement_os_refresh_token");
            }
          }
        }
      } catch (err) {
        console.error("Failed to restore authentication session:", err);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { data, error } = await authApi.login({ email, password });
      if (error || !data) {
        return { success: false, error: error || "Authentication failed" };
      }

      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setUser(data.user);
      localStorage.setItem("placement_os_access_token", data.access_token);
      localStorage.setItem("placement_os_refresh_token", data.refresh_token);

      const { data: profileData } = await profileApi.getProfile(data.access_token);
      if (profileData) {
        setProfile(profileData);
      }

      return { success: true };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    setIsLoading(true);
    try {
      const { data, error } = await authApi.register({ email, password, full_name: fullName });
      if (error || !data) {
        return { success: false, error: error || "Registration failed" };
      }

      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setUser(data.user);
      localStorage.setItem("placement_os_access_token", data.access_token);
      localStorage.setItem("placement_os_refresh_token", data.refresh_token);

      const { data: profileData } = await profileApi.getProfile(data.access_token);
      if (profileData) {
        setProfile(profileData);
      }

      return { success: true };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    if (token && refreshToken) {
      await authApi.logout(token, refreshToken).catch(() => null);
    }
    setToken(null);
    setRefreshToken(null);
    setUser(null);
    setProfile(null);
    localStorage.removeItem("placement_os_access_token");
    localStorage.removeItem("placement_os_refresh_token");
  };

  const refreshProfile = async () => {
    if (token) {
      const { data } = await profileApi.getProfile(token);
      if (data) {
        setProfile(data);
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
