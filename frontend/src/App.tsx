import { BrowserRouter, Routes, Route } from "react-router-dom";
import KeycloakProvider from "./components/KeycloakProvider";
import Layout from "./components/Layout/Layout";
import Home from "./pages/Home";
import Stock from "./pages/Stock";
import Markets from "./pages/Markets";
import Portfolio from "./pages/Portfolio";
import Screener from "./pages/Screener";
import Alerts from "./pages/Alerts";

function App() {
  return (
    <KeycloakProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/stock/:ticker" element={<Stock />} />
            <Route path="/markets" element={<Markets />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/screener" element={<Screener />} />
            <Route path="/alerts" element={<Alerts />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </KeycloakProvider>
  );
}

export default App;
