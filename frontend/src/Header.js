import React from 'react';

// Header Component with User Profile
const Header = ({ currentUser, onOpenOwnProfile, onLogout, onOpenChat, onBackToMain }) => {
  if (!currentUser) return null;

  const getRoleIcon = (role) => {
    switch(role) {
      case 'clubly_founder': return '👑';
      case 'capo_promoter': return '🎯';
      case 'promoter': return '🎪';
      case 'cliente': return '🎉';
      default: return '👤';
    }
  };

  const getRoleName = (role) => {
    switch(role) {
      case 'clubly_founder': return 'Clubly Founder';
      case 'capo_promoter': return 'Capo Promoter';
      case 'promoter': return 'Promoter';
      case 'cliente': return 'Cliente';
      default: return 'Utente';
    }
  };

  return (
    <header className="bg-gray-900 border-b border-red-600 px-4 py-3 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left side - Logo/Brand */}
        <div className="flex items-center space-x-4">
          <button 
            onClick={onBackToMain}
            className="text-red-500 hover:text-red-400 font-bold text-xl transition-colors"
          >
            🎪 CLUBLY
          </button>
        </div>

        {/* Right side - User Profile */}
        <div className="flex items-center space-x-4">
          {/* Chat Button */}
          <button
            onClick={onOpenChat}
            className="relative bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-bold transition-colors flex items-center space-x-2"
          >
            <span>💬</span>
            <span className="hidden md:inline">Chat</span>
          </button>

          {/* User Profile Section - Clickable */}
          <div 
            onClick={onOpenOwnProfile}
            className="flex items-center space-x-3 bg-gray-800 hover:bg-gray-700 rounded-lg px-3 py-2 cursor-pointer transition-colors border border-gray-700 hover:border-red-500"
          >
            {/* Profile Image */}
            {currentUser.profile_image ? (
              <img 
                src={currentUser.profile_image} 
                alt={`${currentUser.nome} ${currentUser.cognome}`}
                className="w-10 h-10 rounded-full object-cover border-2 border-red-500"
              />
            ) : (
              <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-full flex items-center justify-center border-2 border-red-500">
                <span className="text-white font-bold text-lg">
                  {currentUser.nome?.charAt(0)?.toUpperCase() || '?'}
                </span>
              </div>
            )}
            
            {/* User Info */}
            <div className="hidden md:block">
              <div className="flex items-center space-x-2">
                <span className="text-white font-bold">
                  @{currentUser.username}
                </span>
                <span className="text-lg">{getRoleIcon(currentUser.ruolo)}</span>
              </div>
              <p className="text-gray-400 text-sm">
                {getRoleName(currentUser.ruolo)}
              </p>
            </div>

            {/* Click indicator */}
            <div className="text-gray-400 hover:text-red-400 transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={onLogout}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-bold transition-colors flex items-center space-x-2"
            title="Logout"
          >
            <span>🚪</span>
            <span className="hidden lg:inline">Esci</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;