import React from 'react';
import SpotifyData from './SpotifyData';

const handleLogin = () => {
    window.location.href = 'http://localhost:5000/login';
};

const App = () => {
    return (
        <div>
            <button onClick={handleLogin}>Login with Spotify</button>

            <SpotifyData />
        </div>
    );
};

export default App;