import AppRouter from "./router";
import Navbar from "./components/Navbar";
import AuthProvider from "./contexts/AuthContext";

function App() {
  return (
    <AuthProvider>
      <Navbar />
      <AppRouter />
    </AuthProvider>
  );
}

export default App;
