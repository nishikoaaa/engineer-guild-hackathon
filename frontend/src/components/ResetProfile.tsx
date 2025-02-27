import React from 'react';
import { useNavigate } from 'react-router-dom';

const ProfileEditButton: React.FC = () => {
    const navigate = useNavigate();

    const handleEditClick = () => {
        navigate("/QuestionPage", { state: { mode: "edit" } });
    };

    return (
        <button 
        className="common-button" 
        onClick={handleEditClick}
        >
            アンケート編集
        </button>
    );
};

export default ProfileEditButton;