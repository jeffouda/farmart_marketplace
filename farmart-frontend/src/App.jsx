import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "./app/store"; // Ensure this path is correct
import BrowseAnimals from "./pages/BrowseAnimals";
import AnimalDetails from "./pages/AnimalDetails";

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<BrowseAnimals />} />
            <Route path="/animals/:id" element={<AnimalDetails />} />
          </Routes>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
