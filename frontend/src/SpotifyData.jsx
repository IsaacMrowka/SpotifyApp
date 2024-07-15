import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SpotifyData = () => {
    const [userData, setUserData] = useState(null);

    useEffect(() => {
        axios.get("/api/user")
            .then(res => {
                setUserData(res.data)
            }).catch(err => {
                console.log(err)
            })
    }, []);

    return (
        <div>
            {userData ? (
                <p>User: {userData.display_name}</p>
                
            ) : (
                <p>Loading user data...</p>
            )}
        </div>
    );
};

export default SpotifyData;
