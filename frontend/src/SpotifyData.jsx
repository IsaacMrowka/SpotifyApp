import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SpotifyData = () => {
    const [userData, setUserData] = useState(null);
    const [playlistData, setPlaylistData] = useState(null);
    const [likedData, setLikedData] = useState(null);
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

//set user data
    const fetchData = async (url, setData) => {
        try {
            const res = await axios.get(url);
            setData(res.data);
        } catch (err) {
            console.error(err);
        }
    }

useEffect(() => {
    fetchData('api/user', setUserData);
    fetchData('api/playlists', setPlaylistData);
    fetchData('api/tracks', setLikedData);
})
    const handleSearchChange = (e) =>{
        setQuery(r.target.value)
    }
    
    return (
        <div>
            < input 
                type = "text"
                value = {query}
                onChange = {handleSearchChange}
                placeholder = "Search for songs or artists"
            />
            {/*Rednder user data, playlist data, liked data, and search results */}
            <div>
                {userData && <div>User Data: {JSON.stringify(userData)}</div>}
            </div>
        </div>
    );
};

export default SpotifyData;
