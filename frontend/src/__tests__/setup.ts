import "@testing-library/jest-dom";
import { vi } from "vitest";

vi.mock("@testing-library/jest-dom", () => ({
  ...vi.importActual("@testing-library/jest-dom"),
}));