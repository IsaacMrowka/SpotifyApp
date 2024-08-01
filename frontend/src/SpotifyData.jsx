import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SpotifyData = () => {
    const [userData, setUserData] = useState(null);
    const [playlistData, setPlaylistData] = useState(null);
    const [likedData, setLikedData] = useState(null);
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    const fetchData = async (url, setData) => {
        try {
            const res = await axios.get(url);
            setData(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchData('/api/user', setUserData);
        fetchData('/api/playlists', setPlaylistData);
        fetchData('/api/tracks', setLikedData);
    }, []);

    const handleSearchChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearchSubmit = async (e) => {
        e.preventDefault();
        if (query.trim() === '') return;

        try {
            const res = await axios.get(`/api/search?q=${query}`);
            setResults(res.data.tracks.items);
        } catch (err) {
            console.error('Error fetching search results', err);
        }
    };

    return (
        <div>
            <form onSubmit={handleSearchSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={handleSearchChange}
                    placeholder="Search for songs or artists"
                />
                <button type="submit">Search</button>
            </form>
            {/* Render user data, playlist data, liked data, and search results */}
            <div>
                {userData && <div>User Data: {JSON.stringify(userData)}</div>}
                {playlistData && <div>Playlist Data: {JSON.stringify(playlistData)}</div>}
                {likedData && <div>Liked Data: {JSON.stringify(likedData)}</div>}
                {results.length > 0 && (
                    <div>
                        Search Results:
                        <ul> 
                            <li key={track.id}>
                                    {track.name} by {track.artists.map(artist => artist.name).join(', ')}
                            </li>
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SpotifyData;
