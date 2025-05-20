import React, { useState, useEffect } from 'react';
import { apiService } from './services/api';
import './App.css';

function App() {
  const [subjects, setSubjects] = useState([]);
  const [newSubject, setNewSubject] = useState({
    name: '',
    chapters: [],
    exam_date: '',
    difficulty: 3
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch subjects when component mounts
  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const subjects = await apiService.getSubjects();
      setSubjects(subjects);
      setError(null);
    } catch (err) {
      setError('Failed to fetch subjects');
      console.error('Error fetching subjects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSubject = async () => {
    if (!newSubject.name || !newSubject.exam_date || newSubject.chapters.length === 0) {
      alert('Please fill all required fields');
      return;
    }

    try {
      setLoading(true);
      await apiService.addSubject(newSubject);
      // Refresh the list after adding
      await fetchSubjects();
      setNewSubject({ name: '', chapters: [], exam_date: '', difficulty: 3 });
    } catch (err) {
      setError('Failed to add subject');
      console.error('Error adding subject:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveSubject = async (id) => {
    if (!window.confirm('Are you sure you want to delete this subject?')) {
      return;
    }

    try {
      setLoading(true);
      await apiService.deleteSubject(id);
      // Refresh the list after deletion
      await fetchSubjects();
    } catch (err) {
      setError('Failed to delete subject');
      console.error('Error deleting subject:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Smart Study Planner</h1>
      </header>
      
      <main className="container">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <section className="add-subject-section">
          <h2>Add New Subject</h2>
          <form className="subject-form">
            <div className="form-group">
              <label>Subject Name:</label>
              <input
                type="text"
                value={newSubject.name}
                onChange={(e) => setNewSubject({ ...newSubject, name: e.target.value })}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Chapters:</label>
              <div className="chapters-list">
                {newSubject.chapters.map((chapter, index) => (
                  <div key={index} className="chapter-item">
                    <input
                      type="text"
                      value={chapter}
                      onChange={(e) => {
                        const newChapters = [...newSubject.chapters];
                        newChapters[index] = e.target.value;
                        setNewSubject({ ...newSubject, chapters: newChapters });
                      }}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const newChapters = [...newSubject.chapters];
                        newChapters.splice(index, 1);
                        setNewSubject({ ...newSubject, chapters: newChapters });
                      }}
                      disabled={loading}
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={() => setNewSubject({ ...newSubject, chapters: [...newSubject.chapters, ''] })}
                disabled={loading}
              >
                Add Chapter
              </button>
            </div>

            <div className="form-group">
              <label>Exam Date:</label>
              <input
                type="date"
                value={newSubject.exam_date}
                onChange={(e) => setNewSubject({ ...newSubject, exam_date: e.target.value })}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Difficulty (1-5):</label>
              <select
                value={newSubject.difficulty}
                onChange={(e) => setNewSubject({ ...newSubject, difficulty: parseInt(e.target.value) })}
                disabled={loading}
              >
                <option value="1">1 (Easy)</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5 (Difficult)</option>
              </select>
            </div>

            <button
              type="button"
              onClick={handleAddSubject}
              className="add-subject-btn"
              disabled={loading}
            >
              {loading ? 'Adding...' : 'Add Subject'}
            </button>
          </form>
        </section>

        <section className="subjects-list">
          <h2>Your Subjects</h2>
          {loading && <div className="loading">Loading...</div>}
          {subjects.length === 0 && !loading ? (
            <p>No subjects added yet</p>
          ) : (
            <div className="subjects-grid">
              {subjects.map((subject) => (
                <div key={subject.id} className="subject-card">
                  <h3>{subject.name}</h3>
                  <p><strong>Exam Date:</strong> {subject.exam_date}</p>
                  <p><strong>Difficulty:</strong> {subject.difficulty} / 5</p>
                  <p><strong>Chapters:</strong></p>
                  <ul>
                    {subject.chapters.map((chapter, index) => (
                      <li key={index}>{chapter}</li>
                    ))}
                  </ul>
                  <button
                    type="button"
                    onClick={() => handleRemoveSubject(subject.id)}
                    className="remove-btn"
                    disabled={loading}
                  >
                    {loading ? 'Deleting...' : 'Remove'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
