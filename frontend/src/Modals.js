import React, { useState } from 'react';

// User Profile Modal
export const UserProfileModal = ({ show, onClose, userProfile, isOwnProfile, onEdit }) => {
  if (!show || !userProfile) return null;

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

  // Fix per il problema di chiusura - gestione click sul backdrop
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-purple-600 rounded-xl max-w-2xl w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">👤 Profilo Utente</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-purple-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-6">
            {/* Profile Image */}
            <div className="flex-shrink-0">
              {userProfile.profile_image ? (
                <img 
                  src={userProfile.profile_image} 
                  alt={`${userProfile.nome} ${userProfile.cognome}`}
                  className="w-32 h-32 rounded-full object-cover border-4 border-purple-500"
                />
              ) : (
                <div className="w-32 h-32 bg-gradient-to-br from-purple-600 to-purple-700 rounded-full flex items-center justify-center border-4 border-purple-500">
                  <span className="text-white font-bold text-4xl">
                    {userProfile.nome?.charAt(0)?.toUpperCase() || '?'}
                  </span>
                </div>
              )}
            </div>
            
            {/* User Information */}
            <div className="flex-1 space-y-4 text-center md:text-left">
              <div>
                <h3 className="text-white text-2xl font-bold">
                  {userProfile.nome} {userProfile.cognome}
                </h3>
                <p className="text-purple-400 text-lg font-semibold">
                  @{userProfile.username}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Ruolo</p>
                  <p className="text-white font-semibold flex items-center space-x-2">
                    <span>{getRoleIcon(userProfile.ruolo)}</span>
                    <span>{getRoleName(userProfile.ruolo)}</span>
                  </p>
                </div>
                
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Città</p>
                  <p className="text-white font-semibold">📍 {userProfile.citta}</p>
                </div>
                
                {userProfile.organization && (
                  <div className="bg-gray-800 rounded-lg p-3 md:col-span-2">
                    <p className="text-gray-400 text-sm">Organizzazione</p>
                    <p className="text-white font-semibold">🏢 {userProfile.organization}</p>
                  </div>
                )}
                
                <div className="bg-gray-800 rounded-lg p-3 md:col-span-2">
                  <p className="text-gray-400 text-sm">Membro da</p>
                  <p className="text-white font-semibold">
                    📅 {new Date(userProfile.created_at).toLocaleDateString('it-IT', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
              
              {userProfile.biografia && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-2">Biografia</p>
                  <p className="text-gray-300 leading-relaxed">{userProfile.biografia}</p>
                </div>
              )}

              {/* Edit Button - Always show if this is user's own profile */}
              {isOwnProfile && (
                <div className="mt-6">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit && onEdit();
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-bold transition-colors flex items-center space-x-2 mx-auto md:mx-0"
                    type="button"
                  >
                    <span>✏️</span>
                    <span>Modifica Profilo</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Change Password Modal
export const ChangePasswordModal = ({ show, onClose, onSubmit }) => {
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      alert('Le password non coincidono!');
      return;
    }
    
    if (passwordData.new_password.length < 6) {
      alert('La password deve essere di almeno 6 caratteri!');
      return;
    }
    
    onSubmit({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password
    });
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-yellow-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🔒 Cambia Password</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-yellow-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 mb-6">
            <h4 className="text-yellow-400 font-bold text-sm mb-2">⚠️ Primo Accesso</h4>
            <p className="text-yellow-300 text-xs">
              È necessario cambiare la password temporanea per accedere al sistema.
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-yellow-400 font-bold block mb-2">🔐 Password Attuale</label>
              <input
                type="password"
                placeholder="Inserisci la password temporanea"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-500/20 outline-none transition-all"
                required
              />
            </div>

            <div>
              <label className="text-yellow-400 font-bold block mb-2">🆕 Nuova Password</label>
              <input
                type="password"
                placeholder="Inserisci la nuova password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-500/20 outline-none transition-all"
                required
                minLength="6"
              />
            </div>

            <div>
              <label className="text-yellow-400 font-bold block mb-2">✅ Conferma Password</label>
              <input
                type="password"
                placeholder="Conferma la nuova password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-500/20 outline-none transition-all"
                required
                minLength="6"
              />
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-yellow-600 to-yellow-700 hover:from-yellow-700 hover:to-yellow-800 text-black py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🔒 Cambia Password
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Edit Organization Modal 
export const EditOrganizationModal = ({ show, onClose, organization, availableCapoPromoters = [], onSubmit }) => {
  const [orgData, setOrgData] = useState({
    capo_promoter_id: ''
  });

  // Initialize form data when organization changes
  React.useEffect(() => {
    if (organization) {
      setOrgData({
        capo_promoter_id: organization.capo_promoter_id || ''
      });
    }
  }, [organization]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(organization.id, orgData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show || !organization) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-purple-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">✏️ Modifica Organizzazione</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-purple-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>

          <div className="bg-purple-900/30 border border-purple-600 rounded-lg p-4 mb-6">
            <h4 className="text-purple-400 font-bold text-sm mb-2">🏢 Organizzazione</h4>
            <p className="text-purple-300 text-sm">
              <strong>Nome:</strong> {organization.name}
            </p>
            <p className="text-purple-300 text-sm">
              <strong>Città:</strong> {organization.location}
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-purple-400 font-bold block mb-2">🎯 Capo Promoter</label>
              <select
                value={orgData.capo_promoter_id}
                onChange={(e) => setOrgData({...orgData, capo_promoter_id: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
              >
                <option value="">Seleziona capo promoter...</option>
                {availableCapoPromoters.map(capo => (
                  <option key={capo.id} value={capo.id}>
                    {capo.nome} {capo.cognome} (@{capo.username})
                  </option>
                ))}
              </select>
              <p className="text-gray-400 text-xs mt-1">
                Seleziona un capo promoter tra quelli disponibili
              </p>
            </div>
            
            <div className="flex space-x-4 pt-4">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg font-bold transition-colors"
              >
                Annulla
              </button>
              <button 
                type="submit" 
                className="flex-1 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white py-3 rounded-lg font-bold transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                💾 Salva Modifiche
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};


// Edit Organization Modal 
export const EditOrganizationModal = ({ show, onClose, organization, availableCapoPromoters = [], onSubmit }) => {
  const [orgData, setOrgData] = useState({
    capo_promoter_id: ''
  });

  // Initialize form data when organization changes
  React.useEffect(() => {
    if (organization) {
      setOrgData({
        capo_promoter_id: organization.capo_promoter_id || ''
      });
    }
  }, [organization]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(organization.id, orgData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show || !organization) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-purple-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">✏️ Modifica Organizzazione</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-purple-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>

          <div className="bg-purple-900/30 border border-purple-600 rounded-lg p-4 mb-6">
            <h4 className="text-purple-400 font-bold text-sm mb-2">🏢 Organizzazione</h4>
            <p className="text-purple-300 text-sm">
              <strong>Nome:</strong> {organization.name}
            </p>
            <p className="text-purple-300 text-sm">
              <strong>Città:</strong> {organization.location}
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-purple-400 font-bold block mb-2">🎯 Capo Promoter</label>
              <select
                value={orgData.capo_promoter_id}
                onChange={(e) => setOrgData({...orgData, capo_promoter_id: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
              >
                <option value="">Seleziona capo promoter...</option>
                {availableCapoPromoters.map(capo => (
                  <option key={capo.id} value={capo.id}>
                    {capo.nome} {capo.cognome} (@{capo.username})
                  </option>
                ))}
              </select>
              <p className="text-gray-400 text-xs mt-1">
                Seleziona un capo promoter tra quelli disponibili
              </p>
            </div>
            
            <div className="flex space-x-4 pt-4">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg font-bold transition-colors"
              >
                Annulla
              </button>
              <button 
                type="submit" 
                className="flex-1 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white py-3 rounded-lg font-bold transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                💾 Salva Modifiche
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// User Search Modal
export const UserSearchModal = ({ show, onClose, onSearch, searchResults, onViewProfile }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const handleSearch = () => {
    const searchParams = {
      search_term: searchTerm,
      role_filter: roleFilter || null,
      creation_date_from: dateFrom || null,
      creation_date_to: dateTo || null
    };
    onSearch(searchParams);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-purple-600 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🔍 Ricerca Utenti Clubly</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-purple-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          {/* Search Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <input
              type="text"
              placeholder="Cerca per nome, cognome o username..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
            
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            >
              <option value="">Tutti i ruoli</option>
              <option value="cliente">🎉 Cliente</option>
              <option value="promoter">🎪 Promoter</option>
              <option value="capo_promoter">🎯 Capo Promoter</option>
              <option value="clubly_founder">👑 Clubly Founder</option>
            </select>
            
            <input
              type="date"
              placeholder="Data inizio"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
            
            <input
              type="date"
              placeholder="Data fine"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
          </div>
          
          <button 
            onClick={handleSearch}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-bold transition-colors mb-6"
            type="button"
          >
            🔍 Cerca
          </button>
          
          {/* Search Results */}
          <div className="space-y-4">
            <h3 className="text-white text-xl font-bold">Risultati ({searchResults.length})</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map(user => (
                <div 
                  key={user.id}
                  onClick={() => onViewProfile(user.id)}
                  className="bg-gray-800 rounded-lg p-4 cursor-pointer hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {user.profile_image ? (
                      <img 
                        src={user.profile_image} 
                        alt={user.nome}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">{user.nome?.charAt(0)}</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="text-white font-bold">@{user.username}</p>
                      <p className="text-gray-300 text-sm">{user.nome} {user.cognome}</p>
                      <p className="text-gray-400 text-xs">
                        {user.ruolo === 'clubly_founder' ? '👑' : 
                         user.ruolo === 'capo_promoter' ? '🎯' :
                         user.ruolo === 'promoter' ? '🎪' : '🎉'} {user.citta}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {searchResults.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <p>Nessun utente trovato</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Create Event Modal - MIGLIORATO con locandina eventi e validazione date
export const CreateEventModal = ({ show, onClose, onSubmit, userRole }) => {
  const [eventData, setEventData] = useState({
    name: '',
    date: '',
    start_time: '',
    location: '',
    organization: '',
    end_time: '',
    lineup: [],
    location_address: '',
    total_tables: '',
    table_types: '',
    max_party_size: '10',
    event_poster: ''
  });

  const [newDj, setNewDj] = useState('');
  const [posterPreview, setPosterPreview] = useState(null);

  // Add DJ to lineup
  const addDj = () => {
    if (newDj.trim()) {
      setEventData({
        ...eventData,
        lineup: [...eventData.lineup, newDj.trim()]
      });
      setNewDj('');
    }
  };

  // Remove DJ from lineup
  const removeDj = (index) => {
    const newLineup = eventData.lineup.filter((_, i) => i !== index);
    setEventData({...eventData, lineup: newLineup});
  };

  // Handle poster upload
  const handlePosterUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setEventData({...eventData, event_poster: reader.result});
        setPosterPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate date and time are not in the past
    const eventDateTime = new Date(`${eventData.date}T${eventData.start_time}`);
    const now = new Date();
    if (eventDateTime <= now) {
      alert('Non puoi creare eventi con date o orari nel passato!');
      return;
    }
    
    const formattedData = {
      ...eventData,
      table_types: eventData.table_types ? eventData.table_types.split(',').map(type => type.trim()).filter(type => type) : [],
      total_tables: parseInt(eventData.total_tables) || 0,
      max_party_size: parseInt(eventData.max_party_size) || 10
    };
    onSubmit(formattedData, userRole);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-red-600 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🎉 Crea Nuovo Evento</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-red-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Event Poster Upload */}
            <div className="space-y-2">
              <label className="text-red-400 font-bold block">🖼️ Locandina Evento</label>
              <div className="flex items-center space-x-4">
                {posterPreview && (
                  <img 
                    src={posterPreview} 
                    alt="Preview locandina" 
                    className="w-24 h-32 object-cover rounded-lg border-2 border-red-500"
                  />
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handlePosterUpload}
                  className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-red-600 file:text-white hover:file:bg-red-700 file:cursor-pointer"
                />
              </div>
              <p className="text-gray-400 text-xs">
                {userRole === 'clubly_founder' 
                  ? '👑 Come Clubly Founder puoi aggiungere la locandina' 
                  : '🎯 Il Capo Promoter potrà modificare la locandina successivamente'
                }
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Required Fields */}
              <div className="col-span-full">
                <label className="text-red-400 font-bold block mb-2">📝 Campi Obbligatori</label>
              </div>
              
              <input
                type="text"
                placeholder="Nome dell'evento *"
                value={eventData.name}
                onChange={(e) => setEventData({...eventData, name: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              <input
                type="date"
                value={eventData.date}
                onChange={(e) => setEventData({...eventData, date: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
                min={new Date().toISOString().split('T')[0]}
              />
              
              {/* ORARIO LIBERO - input time invece di select */}
              <div>
                <label className="text-red-400 font-bold block mb-1">🕘 Orario di inizio *</label>
                <input
                  type="time"
                  value={eventData.start_time}
                  onChange={(e) => setEventData({...eventData, start_time: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                  required
                />
                <p className="text-gray-400 text-xs mt-1">Puoi inserire qualsiasi orario</p>
              </div>
              
              <input
                type="text"
                placeholder="Locale *"
                value={eventData.location}
                onChange={(e) => setEventData({...eventData, location: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              {/* Optional Fields */}
              <div className="col-span-full mt-6">
                <label className="text-blue-400 font-bold block mb-2">⭐ Campi Facoltativi</label>
              </div>
              
              <input
                type="text"
                placeholder="Organizzazione"
                value={eventData.organization}
                onChange={(e) => setEventData({...eventData, organization: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              {/* ORARIO FINE ANCHE LIBERO */}
              <div>
                <label className="text-blue-400 font-bold block mb-1">🕘 Orario di fine</label>
                <input
                  type="time"
                  value={eventData.end_time}
                  onChange={(e) => setEventData({...eventData, end_time: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                />
              </div>
              
              {/* DESIGN DJ MIGLIORATO */}
              <div className="col-span-full">
                <label className="text-blue-400 font-bold block mb-2">🎵 Line-up DJ</label>
                
                {/* Current DJ List */}
                {eventData.lineup.length > 0 && (
                  <div className="mb-4 space-y-2">
                    <h4 className="text-sm text-gray-400">DJ in lineup:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {eventData.lineup.map((dj, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2 border border-blue-500/20">
                          <div className="flex items-center space-x-2">
                            <span className="text-blue-400">🎧</span>
                            <span className="text-white">{dj}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeDj(index)}
                            className="text-red-400 hover:text-red-300 text-sm transition-colors"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Add New DJ */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Nome DJ (es. DJ Marco)"
                    value={newDj}
                    onChange={(e) => setNewDj(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDj())}
                    className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={addDj}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-bold transition-colors flex items-center space-x-1"
                  >
                    <span>➕</span>
                    <span className="hidden md:inline">Aggiungi</span>
                  </button>
                </div>
                <div className="flex items-center space-x-2 mt-2">
                  <span className="text-gray-400 text-xs">💡 Suggerimento:</span>
                  <span className="text-blue-400 text-xs">Aggiungi un DJ alla volta per una gestione migliore</span>
                </div>
              </div>
              
              <input
                type="text"
                placeholder="Indirizzo del locale"
                value={eventData.location_address}
                onChange={(e) => setEventData({...eventData, location_address: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              <input
                type="number"
                placeholder="Numero tavoli disponibili"
                value={eventData.total_tables}
                onChange={(e) => setEventData({...eventData, total_tables: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                min="0"
              />
              
              <input
                type="text"
                placeholder="Tipi di tavoli (separati da virgola)"
                value={eventData.table_types}
                onChange={(e) => setEventData({...eventData, table_types: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              <input
                type="number"
                placeholder="Max persone per tavolo"
                value={eventData.max_party_size}
                onChange={(e) => setEventData({...eventData, max_party_size: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                min="1"
                max="20"
              />
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🎉 Crea Evento
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Create Organization Modal - REMOVED capo_promoter_username field
export const CreateOrganizationModal = ({ show, onClose, onSubmit }) => {
  const [orgData, setOrgData] = useState({
    name: '',
    location: ''
    // Removed capo_promoter_username - will be assigned later via edit
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(orgData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-blue-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🏢 Crea Organizzazione</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-blue-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nome organizzazione"
              value={orgData.name}
              onChange={(e) => setOrgData({...orgData, name: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="text"
              placeholder="Città"
              value={orgData.location}
              onChange={(e) => setOrgData({...orgData, location: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🏢 Crea Organizzazione
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Create Capo Promoter Modal - UPDATED con dropdown organizzazioni
export const CreateCapoPromoterModal = ({ show, onClose, onSubmit, organizations = [] }) => {
  const [userData, setUserData] = useState({
    nome: '',
    email: '',
    organization: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(userData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-green-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🎯 Crea Capo Promoter</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-green-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nome"
              value={userData.nome}
              onChange={(e) => setUserData({...userData, nome: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="email"
              placeholder="Email"
              value={userData.email}
              onChange={(e) => setUserData({...userData, email: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all"
              required
            />
            
            <div>
              <label className="text-green-400 font-bold block mb-2">🏢 Organizzazione</label>
              <select
                value={userData.organization}
                onChange={(e) => setUserData({...userData, organization: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all"
              >
                <option value="">Seleziona organizzazione...</option>
                {organizations.map(org => (
                  <option key={org.id} value={org.name}>{org.name} - {org.location}</option>
                ))}
              </select>
              <p className="text-gray-400 text-xs mt-1">Opzionale: puoi assegnarla successivamente</p>
            </div>
            
            <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-3">
              <p className="text-yellow-400 text-sm">
                ⚠️ Verrà generata una password temporanea che l'utente dovrà cambiare al primo accesso.
              </p>
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🎯 Crea Capo Promoter
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Create Promoter Modal (for Capo Promoter)
export const CreatePromoterModal = ({ show, onClose, onSubmit }) => {
  const [userData, setUserData] = useState({
    nome: '',
    email: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(userData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-blue-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🎪 Crea Promoter</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-blue-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nome"
              value={userData.nome}
              onChange={(e) => setUserData({...userData, nome: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="email"
              placeholder="Email"
              value={userData.email}
              onChange={(e) => setUserData({...userData, email: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-3">
              <p className="text-yellow-400 text-sm">
                ⚠️ Verrà generata una password temporanea che l'utente dovrà cambiare al primo accesso.
              </p>
              <p className="text-blue-400 text-sm mt-2">
                📝 Il promoter sarà assegnato automaticamente alla tua organizzazione.
              </p>
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🎪 Crea Promoter
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Organization Details Modal
export const OrganizationDetailsModal = ({ show, onClose, organization, onViewProfile }) => {
  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show || !organization) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-blue-600 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🏢 {organization.name}</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-blue-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Organization Info */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-blue-400 font-bold text-xl mb-4">📍 Informazioni</h3>
              <div className="space-y-3">
                <p className="text-gray-300"><span className="text-gray-400">Nome:</span> {organization.name}</p>
                <p className="text-gray-300"><span className="text-gray-400">Città:</span> {organization.location}</p>
                <p className="text-gray-300"><span className="text-gray-400">Membri:</span> {organization.members?.length || 0}</p>
                <p className="text-gray-300"><span className="text-gray-400">Eventi:</span> {organization.events?.length || 0}</p>
                <p className="text-gray-300">
                  <span className="text-gray-400">Creata il:</span> {' '}
                  {new Date(organization.created_at).toLocaleDateString('it-IT')}
                </p>
              </div>
            </div>
            
            {/* Members */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-green-400 font-bold text-xl mb-4">👥 Membri ({organization.members?.length || 0})</h3>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {organization.members?.map(member => (
                  <div 
                    key={member.id}
                    onClick={() => onViewProfile(member.id)}
                    className="flex items-center space-x-3 bg-gray-700 rounded-lg p-3 cursor-pointer hover:bg-gray-600 transition-colors"
                  >
                    {member.profile_image ? (
                      <img 
                        src={member.profile_image} 
                        alt={member.nome}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">{member.nome?.charAt(0)}</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="text-white font-bold">@{member.username}</p>
                      <p className="text-gray-300 text-sm">{member.nome} {member.cognome}</p>
                      <p className="text-gray-400 text-xs">
                        {member.ruolo === 'capo_promoter' ? '🎯 Capo Promoter' : '🎪 Promoter'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Events */}
          <div className="mt-6 bg-gray-800 rounded-lg p-6">
            <h3 className="text-red-400 font-bold text-xl mb-4">🎉 Eventi ({organization.events?.length || 0})</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {organization.events?.map(event => (
                <div key={event.id} className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-white font-bold">{event.name}</h4>
                  <p className="text-gray-300 text-sm">📅 {event.date}</p>
                  <p className="text-gray-300 text-sm">📍 {event.location}</p>
                  <p className="text-gray-300 text-sm">🕘 {event.start_time}</p>
                </div>
              ))}
            </div>
            
            {organization.events?.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <p>Nessun evento trovato per questa organizzazione</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Edit Profile Modal for own profile editing
export const EditProfileModal = ({ show, onClose, currentUser, onSubmit }) => {
  const [profileData, setProfileData] = useState({
    nome: '',
    username: '',
    biografia: '',
    citta: ''
  });

  // Initialize form data when user changes
  React.useEffect(() => {
    if (currentUser) {
      setProfileData({
        nome: currentUser.nome || '',
        username: currentUser.username || '',
        biografia: currentUser.biografia || '',
        citta: currentUser.citta || ''
      });
    }
  }, [currentUser]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(profileData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show || !currentUser) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-blue-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">✏️ Modifica Profilo</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-blue-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>

          <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4 mb-6">
            <h4 className="text-blue-400 font-bold text-sm mb-2">📝 Campi Modificabili</h4>
            <p className="text-blue-300 text-xs">
              Puoi modificare: <strong>Nome, Username, Biografia e Città</strong>
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-blue-400 font-bold block mb-2">👤 Nome</label>
              <input
                type="text"
                placeholder="Il tuo nome"
                value={profileData.nome}
                onChange={(e) => setProfileData({...profileData, nome: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                required
              />
            </div>

            <div>
              <label className="text-blue-400 font-bold block mb-2">🆔 Username</label>
              <input
                type="text"
                placeholder="Il tuo username"
                value={profileData.username}
                onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                required
              />
              <p className="text-gray-400 text-xs mt-1">L'username deve essere unico</p>
            </div>

            <div>
              <label className="text-blue-400 font-bold block mb-2">📍 Città</label>
              <input
                type="text"
                placeholder="La tua città"
                value={profileData.citta}
                onChange={(e) => setProfileData({...profileData, citta: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                required
              />
            </div>

            <div>
              <label className="text-blue-400 font-bold block mb-2">📝 Biografia</label>
              <textarea
                placeholder="Racconta qualcosa di te..."
                value={profileData.biografia}
                onChange={(e) => setProfileData({...profileData, biografia: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                rows="3"
              />
            </div>
            
            <div className="flex space-x-4 pt-4">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg font-bold transition-colors"
              >
                Annulla
              </button>
              <button 
                type="submit" 
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3 rounded-lg font-bold transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                💾 Salva Modifiche
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Edit Event Modal - MIGLIORATO con orario libero
export const EditEventModal = ({ show, onClose, event, onSubmit }) => {
  const [eventData, setEventData] = useState({
    name: '',
    lineup: [],
    start_time: '',
    end_time: '',
    guests: []
  });

  const [newDj, setNewDj] = useState('');
  const [newGuest, setNewGuest] = useState('');

  // Initialize form data when event changes
  React.useEffect(() => {
    if (event) {
      setEventData({
        name: event.name || '',
        lineup: Array.isArray(event.lineup) ? event.lineup : [],
        start_time: event.start_time || '',
        end_time: event.end_time || '',
        guests: Array.isArray(event.guests) ? event.guests : []
      });
    }
  }, [event]);

  // Add DJ to lineup
  const addDj = () => {
    if (newDj.trim()) {
      setEventData({
        ...eventData,
        lineup: [...eventData.lineup, newDj.trim()]
      });
      setNewDj('');
    }
  };

  // Remove DJ from lineup
  const removeDj = (index) => {
    const newLineup = eventData.lineup.filter((_, i) => i !== index);
    setEventData({...eventData, lineup: newLineup});
  };

  // Add Guest
  const addGuest = () => {
    if (newGuest.trim()) {
      setEventData({
        ...eventData,
        guests: [...eventData.guests, newGuest.trim()]
      });
      setNewGuest('');
    }
  };

  // Remove Guest
  const removeGuest = (index) => {
    const newGuests = eventData.guests.filter((_, i) => i !== index);
    setEventData({...eventData, guests: newGuests});
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(event.id, eventData);
  };

  // Fix per il problema di chiusura
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!show || !event) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-gray-900 border border-orange-600 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">✏️ Modifica Evento</h2>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="text-gray-400 hover:text-orange-400 text-2xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
              type="button"
            >
              ✕
            </button>
          </div>

          {/* Event Info */}
          <div className="bg-gray-800 rounded-lg p-4 mb-6">
            <h3 className="text-orange-400 font-bold mb-2">📋 Informazioni Evento</h3>
            <p className="text-gray-300 text-sm"><span className="text-gray-400">Data:</span> {event.date}</p>
            <p className="text-gray-300 text-sm"><span className="text-gray-400">Locale:</span> {event.location}</p>
            <p className="text-gray-300 text-sm"><span className="text-gray-400">Organizzazione:</span> {event.organization}</p>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 mb-6">
            <h4 className="text-yellow-400 font-bold text-sm mb-2">⚠️ Permessi di Modifica</h4>
            <p className="text-yellow-300 text-xs">
              Come Capo Promoter puoi modificare: <strong>Nome evento, Orario di inizio, Orario di fine, Line-up DJ e Guest</strong>
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-4">
              <div>
                <label className="text-orange-400 font-bold block mb-2">📝 Nome Evento</label>
                <input
                  type="text"
                  placeholder="Nome dell'evento"
                  value={eventData.name}
                  onChange={(e) => setEventData({...eventData, name: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                  required
                />
              </div>

              {/* DESIGN DJ MIGLIORATO */}
              <div>
                <label className="text-orange-400 font-bold block mb-2">🎵 Line-up DJ</label>
                
                {/* Current DJ List */}
                {eventData.lineup.length > 0 && (
                  <div className="mb-4 space-y-2">
                    <h4 className="text-sm text-gray-400">DJ in lineup:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {eventData.lineup.map((dj, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2 border border-orange-500/20">
                          <div className="flex items-center space-x-2">
                            <span className="text-orange-400">🎧</span>
                            <span className="text-white">{dj}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeDj(index)}
                            className="text-red-400 hover:text-red-300 text-sm transition-colors"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Add New DJ */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Nome DJ (es. DJ Marco)"
                    value={newDj}
                    onChange={(e) => setNewDj(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDj())}
                    className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={addDj}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-lg font-bold transition-colors flex items-center space-x-1"
                  >
                    <span>➕</span>
                    <span className="hidden md:inline">Aggiungi</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-orange-400 font-bold block mb-2">🕘 Orario di Inizio</label>
                  <input
                    type="time"
                    value={eventData.start_time}
                    onChange={(e) => setEventData({...eventData, start_time: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                    required
                  />
                  <p className="text-gray-400 text-xs mt-1">Puoi inserire qualsiasi orario</p>
                </div>

                <div>
                  <label className="text-orange-400 font-bold block mb-2">🕘 Orario di Fine</label>
                  <input
                    type="time"
                    value={eventData.end_time}
                    onChange={(e) => setEventData({...eventData, end_time: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                  />
                </div>
              </div>

              {/* DESIGN GUEST MIGLIORATO */}
              <div>
                <label className="text-orange-400 font-bold block mb-2">⭐ Guest Speciali</label>
                
                {/* Current Guest List */}
                {eventData.guests.length > 0 && (
                  <div className="mb-4 space-y-2">
                    <h4 className="text-sm text-gray-400">Guest speciali:</h4>
                    <div className="grid grid-cols-1 gap-2">
                      {eventData.guests.map((guest, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2 border border-orange-500/20">
                          <div className="flex items-center space-x-2">
                            <span className="text-orange-400">⭐</span>
                            <span className="text-white">{guest}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeGuest(index)}
                            className="text-red-400 hover:text-red-300 text-sm transition-colors"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Add New Guest */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Nome guest speciale"
                    value={newGuest}
                    onChange={(e) => setNewGuest(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addGuest())}
                    className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={addGuest}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-lg font-bold transition-colors flex items-center space-x-1"
                  >
                    <span>➕</span>
                    <span className="hidden md:inline">Aggiungi</span>
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-4 pt-4">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg font-bold transition-colors"
              >
                Annulla
              </button>
              <button 
                type="submit" 
                className="flex-1 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white py-3 rounded-lg font-bold transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                💾 Salva Modifiche
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};