"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi, getToken, setToken } from "@/lib/api";
import type { User } from "@/types/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // 초기 로드: 토큰이 있으면 사용자 정보 가져오기
  useEffect(() => {
    const token = getToken();
    if (token) {
      authApi
        .me()
        .then((user) => setUser(user))
        .catch(() => {
          // 토큰이 유효하지 않으면 제거
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    setToken(response.token.access_token);
    setUser(response.user);
    router.push("/dashboard");
  };

  const register = async (email: string, name: string, password: string) => {
    const user = await authApi.register({ email, name, password });
    // 회원가입 후 자동 로그인
    await login(email, password);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
