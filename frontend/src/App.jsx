import React, {useState, useEffect} from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import SpotifyData from './SpotifyData';
import axios from 'axios';
import './App.css';

const App = () => {
    const [userData, setUserData] = useState(null);

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const res = await axios.get('http://localhost:5000/api/user', { withCredentials: true });
                setUserData(res.data);
            }
            catch (err) { console.error('Error in aqcuiring user data', err)}
        }
        fetchUserData();
    }, []);

    const handleLogin = () => {
        window.location.href = 'http://localhost:5000/login';
    };

    return (
        <Router>
            <div>
                <header>
                    <div className="user-data">
                            {userData ? (
                                <div>
                                    <img src={userData.images[0].url}/>
                                    <h2>{userData.display_name}</h2>
                                </div>
                            ) : (
                                <button className="login-button" onClick={handleLogin}>Login with Spotify</button>
                            )}
                        </div>
                </header>
                <main>
                    <Routes>
                        <Route path="/" element={<SpotifyData userData={userData}/>} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
};

export default App;
