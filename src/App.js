import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./components/Home/Home";
import UserAccount from "./components/Account/Account";

function App() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/account" element={<UserAccount />} />
        </Routes>
    );
}

export default App;
