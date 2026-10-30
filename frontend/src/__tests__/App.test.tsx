/// <reference types="@testing-library/jest-dom" />
import { render, screen, waitFor } from "@testing-library/react";
import App from "../App";
describe("App", () => {
  it("renders the application title", () => {
    render(<App />);
    expect(screen.getByText(/vector-engine-alan-vo/i)).toBeInTheDocument();
  });

  it("renders loading state initially", () => {
    render(<App />);
    const loadingElements = screen.getAllByText(/checking/i);
    expect(loadingElements.length).toBe(2);
  });

  it("renders footer with author attribution after load", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Alan Vo/i)).toBeInTheDocument();
    });
  });
});