import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("./keycloak", () => ({
  default: {
    init: vi.fn().mockResolvedValue(true),
    tokenParsed: {
      preferred_username: "testuser",
      realm_access: { roles: ["user"] },
    },
    token: "fake-token",
    onTokenExpired: null,
    logout: vi.fn(),
    updateToken: vi.fn().mockResolvedValue(true),
  },
}));

vi.mock("./services/api", () => ({
  getIndices: vi.fn().mockResolvedValue([]),
  getStock: vi.fn().mockRejectedValue(new Error("mock")),
  default: { interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } } },
}));

import App from "./App";

test("renders home page when authenticated", async () => {
  render(<App />);
  const heading = await screen.findByText("Investissement");
  expect(heading).toBeInTheDocument();
});

test("displays username when authenticated", async () => {
  render(<App />);
  const username = await screen.findByText(/testuser/);
  expect(username).toBeInTheDocument();
});
