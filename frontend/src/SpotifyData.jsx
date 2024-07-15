import React, { useEffect, useState } from 'react';

const SpotifyData = () => {
    const [userData, setUserData] = useState(null);
    const [playlistsData, setPlaylistsData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const handleLogin = () => {
        window.location.href = 'http://localhost:5000/login';
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const userResponse = await fetch('http://localhost:5000/user');
                if (!userResponse.ok) {
                    throw new Error('Failed to fetch user data');
                }
                const user = await userResponse.json();
                setUserData(user);

                const playlistsResponse = await fetch('http://localhost:5000/playlists');
                if (!playlistsResponse.ok) {
                    throw new Error('Failed to fetch playlists data');
                }
                const playlists = await playlistsResponse.json();
                setPlaylistsData(playlists);

                setLoading(false);
            } catch (error) {
                setError(error.message);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div>
                <button onClick={handleLogin}>Login with Spotify</button>
                <div>Loading...</div>
            </div>
        );
    }

    return (
        <div>
            <button onClick={handleLogin}>Login with Spotify</button>
            <h1>User: {userData.display_name}</h1>
            <h2>Playlists:</h2>
            <ul>
                {playlistsData.items.map((playlist, index) => (
                    <li key={index}>{playlist.name}</li>
                ))}
            </ul>
        </div>
    );
};

export default SpotifyData;
