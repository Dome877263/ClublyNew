import React from 'react';

// Header Component with User Profile and Notifications
const Header = ({ currentUser, currentView, setCurrentView, onLogout, onOpenProfile, notificationsCount = 0 }) => {
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

  // Navigate based on user role
  const navigateToDashboard = () => {
    switch(currentUser.ruolo) {
      case 'clubly_founder':
        setCurrentView('clubly-founder');
        break;
      case 'capo_promoter':
        setCurrentView('capo-promoter');
        break;
      case 'promoter':
        setCurrentView('promoter');
        break;
      default:
        setCurrentView('main');
    }
  };

  return (
    <header className="bg-gray-900 border-b border-red-600 px-4 py-3 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left side - Logo/Brand */}
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => setCurrentView('main')}
            className="text-red-500 hover:text-red-400 font-bold text-xl transition-colors"
          >
            🎪 CLUBLY
          </button>
          
          {/* Navigation */}
          {currentUser.ruolo !== 'cliente' && (
            <div className="hidden md:flex items-center space-x-2">
              <button
                onClick={() => setCurrentView('main')}
                className={`px-3 py-1 rounded transition-colors ${
                  currentView === 'main' ? 'bg-red-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                🏠 Home
              </button>
              <button
                onClick={navigateToDashboard}
                className={`px-3 py-1 rounded transition-colors ${
                  currentView !== 'main' ? 'bg-red-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                📊 Dashboard
              </button>
            </div>
          )}
        </div>

        {/* Right side - User Profile */}
        <div className="flex items-center space-x-4">
          {/* Chat Button with Notifications Badge */}
          <button
            onClick={() => setCurrentView('main')} // This will be handled by chat modal in main app
            className="relative bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-bold transition-colors flex items-center space-x-2"
          >
            <span>💬</span>
            <span className="hidden md:inline">Chat</span>
            {/* Notifications Badge */}
            {notificationsCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-6 w-6 flex items-center justify-center border-2 border-gray-900 animate-pulse">
                {notificationsCount > 99 ? '99+' : notificationsCount}
              </span>
            )}
          </button>

          {/* User Profile Section - Clickable */}
          <div 
            onClick={onOpenProfile}
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
                  {currentUser.nome} {currentUser.cognome}
                </span>
                <span className="text-lg">{getRoleIcon(currentUser.ruolo)}</span>
              </div>
              <p className="text-gray-400 text-sm">
                @{currentUser.username} • {getRoleName(currentUser.ruolo)}
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