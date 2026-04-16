import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import keycloak from "../keycloak";

interface KeycloakContextType {
  authenticated: boolean;
  token: string | undefined;
  username: string;
  roles: string[];
  logout: () => void;
}

const KeycloakContext = createContext<KeycloakContextType>({
  authenticated: false,
  token: undefined,
  username: "",
  roles: [],
  logout: () => {},
});

export function useKeycloak() {
  return useContext(KeycloakContext);
}

interface Props {
  children: ReactNode;
}

export default function KeycloakProvider({ children }: Props) {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    keycloak
      .init({ onLoad: "login-required", checkLoginIframe: false })
      .then((auth) => {
        setAuthenticated(auth);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Keycloak init failed", err);
        setLoading(false);
      });

    keycloak.onTokenExpired = () => {
      keycloak.updateToken(30).catch(() => keycloak.logout());
    };
  }, []);

  if (loading) {
    return <div>Chargement...</div>;
  }

  if (!authenticated) {
    return <div>Non authentifié. Redirection...</div>;
  }

  const tokenParsed = keycloak.tokenParsed;
  const username = tokenParsed?.preferred_username ?? "";
  const roles: string[] = tokenParsed?.realm_access?.roles ?? [];

  const value: KeycloakContextType = {
    authenticated,
    token: keycloak.token,
    username,
    roles,
    logout: () => keycloak.logout(),
  };

  return (
    <KeycloakContext.Provider value={value}>
      {children}
    </KeycloakContext.Provider>
  );
}
