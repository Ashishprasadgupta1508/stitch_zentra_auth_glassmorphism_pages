(function () {
  const NOTES_STORAGE_KEY = 'zentra-uploaded-notes';

  function loadNotes() {
    try {
      const stored = localStorage.getItem(NOTES_STORAGE_KEY);
      if (!stored) return [];
      const parsed = JSON.parse(stored);
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      console.warn('Unable to load notes:', error);
      return [];
    }
  }

  function saveNotes(notes) {
    localStorage.setItem(NOTES_STORAGE_KEY, JSON.stringify(notes));
    return notes;
  }

  function addNote(note) {
    const notes = loadNotes();
    const nextNote = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      ...note
    };
    const nextNotes = [nextNote, ...notes];
    saveNotes(nextNotes);
    return nextNotes;
  }

  function deleteNote(noteId) {
    const notes = loadNotes().filter((note) => note.id !== noteId);
    saveNotes(notes);
    return notes;
  }

  function getGroupedNotes(notes) {
    return notes.reduce((groups, note) => {
      const subject = (note.subject || 'General').trim() || 'General';
      if (!groups[subject]) groups[subject] = [];
      groups[subject].push(note);
      return groups;
    }, {});
  }

  function formatFileSize(bytes) {
    if (!bytes) return '0 KB';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  }

  window.ZentraNotes = {
    NOTES_STORAGE_KEY,
    loadNotes,
    saveNotes,
    addNote,
    deleteNote,
    getGroupedNotes,
    formatFileSize
  };
})();
