/**
 * VoicePath Demo Songs
 * Pre-scored lyrics with tension/valence values
 * 
 * Coordinate System:
 *   X (Tension):  -1 (calm) to +1 (intense)
 *   Y (Valence):  -1 (negative) to +1 (positive)
 */

const DEMO_SONGS = {
    
    // ═══════════════════════════════════════════════════════════════
    // "A Day in the Life" - Inspired trajectory (abstract recreation)
    // The spiral that descends while pretending to rise
    // ═══════════════════════════════════════════════════════════════
    dayinthelife: {
        title: "A Day in the Life",
        artist: "Kinematic Demo",
        duration: 60, // seconds (compressed demo)
        bpm: 80,
        
        // The semantic envelope - where the trajectory CAN go
        envelope: {
            center: { x: 0, y: 0 },
            radiusX: 0.85,
            radiusY: 0.85
        },
        
        lyrics: [
            // Time (s), lyric text, tension (-1 to 1), valence (-1 to 1)
            { time: 0,    text: "I read the news today...",           tension: -0.3, valence: 0.2 },
            { time: 4,    text: "oh boy",                              tension: -0.2, valence: -0.1 },
            { time: 7,    text: "About a lucky man",                   tension: 0.1,  valence: 0.4 },
            { time: 10,   text: "who made the grade",                  tension: 0.3,  valence: 0.5 },
            { time: 14,   text: "And though the news",                 tension: 0.2,  valence: 0.1 },
            { time: 17,   text: "was rather sad",                      tension: 0.1,  valence: -0.4 },
            { time: 20,   text: "Well, I just had to laugh",           tension: 0.5,  valence: 0.3 },
            { time: 24,   text: "I saw the photograph",                tension: -0.1, valence: -0.2 },
            { time: 28,   text: "...",                                 tension: -0.3, valence: -0.3 },
            
            // Second movement - different feel
            { time: 32,   text: "Woke up",                             tension: 0.2,  valence: 0.1 },
            { time: 34,   text: "fell out of bed",                     tension: 0.4,  valence: -0.1 },
            { time: 36,   text: "Dragged a comb across my head",       tension: 0.3,  valence: 0.0 },
            { time: 40,   text: "Found my way downstairs",             tension: 0.1,  valence: 0.2 },
            { time: 43,   text: "and drank a cup",                     tension: -0.1, valence: 0.3 },
            { time: 46,   text: "Looking up",                          tension: 0.2,  valence: 0.4 },
            { time: 48,   text: "I noticed I was late",                tension: 0.6,  valence: -0.2 },
            
            // Crescendo
            { time: 52,   text: "~ ~ ~",                               tension: 0.8,  valence: 0.0 },
            { time: 55,   text: "~ ~ ~ ~ ~",                           tension: 0.9,  valence: 0.1 },
            
            // Final chord
            { time: 58,   text: "...",                                 tension: 0.0,  valence: -0.5 },
        ]
    },
    
    // ═══════════════════════════════════════════════════════════════
    // Abstract Journey - A pure trajectory demonstration
    // ═══════════════════════════════════════════════════════════════
    abstract: {
        title: "Abstract Journey",
        artist: "Newton Engine",
        duration: 45,
        bpm: 90,
        
        envelope: {
            center: { x: 0, y: 0 },
            radiusX: 0.9,
            radiusY: 0.9
        },
        
        lyrics: [
            { time: 0,    text: "Beginning",                          tension: -0.8, valence: 0.0 },
            { time: 4,    text: "Rising slowly",                      tension: -0.6, valence: 0.3 },
            { time: 8,    text: "Gathering momentum",                 tension: -0.3, valence: 0.5 },
            { time: 12,   text: "The peak approaches",                tension: 0.0,  valence: 0.8 },
            { time: 16,   text: "APEX",                               tension: 0.3,  valence: 0.9 },
            { time: 20,   text: "Tension builds",                     tension: 0.6,  valence: 0.6 },
            { time: 24,   text: "Maximum intensity",                  tension: 0.9,  valence: 0.3 },
            { time: 28,   text: "The turn",                           tension: 0.7,  valence: -0.2 },
            { time: 32,   text: "Falling",                            tension: 0.4,  valence: -0.5 },
            { time: 36,   text: "Descent",                            tension: 0.1,  valence: -0.7 },
            { time: 40,   text: "Return to calm",                     tension: -0.5, valence: -0.3 },
            { time: 44,   text: "...",                                tension: -0.8, valence: 0.0 },
        ]
    },
    
    // ═══════════════════════════════════════════════════════════════
    // Descending Spiral - The "A Day in the Life" shape made explicit
    // ═══════════════════════════════════════════════════════════════
    spiral: {
        title: "Descending Spiral",
        artist: "Verified Trajectory",
        duration: 50,
        bpm: 70,
        
        envelope: {
            center: { x: 0, y: -0.2 },  // Slightly negative center
            radiusX: 0.8,
            radiusY: 0.7
        },
        
        lyrics: [
            // First loop
            { time: 0,    text: "Circle one begins",                  tension: -0.5, valence: 0.3 },
            { time: 3,    text: "Rising on the surface",              tension: -0.2, valence: 0.5 },
            { time: 6,    text: "Seeming to climb",                   tension: 0.2,  valence: 0.4 },
            { time: 9,    text: "But underneath...",                  tension: 0.4,  valence: 0.1 },
            { time: 12,   text: "...we descend",                      tension: 0.3,  valence: -0.2 },
            
            // Second loop (lower)
            { time: 16,   text: "Circle two",                         tension: -0.4, valence: 0.1 },
            { time: 19,   text: "The pattern repeats",                tension: -0.1, valence: 0.3 },
            { time: 22,   text: "Higher they say",                    tension: 0.3,  valence: 0.2 },
            { time: 25,   text: "Lower we go",                        tension: 0.5,  valence: -0.3 },
            { time: 28,   text: "Always down",                        tension: 0.2,  valence: -0.4 },
            
            // Third loop (lowest)
            { time: 32,   text: "Final circle",                       tension: -0.3, valence: -0.1 },
            { time: 35,   text: "The illusion fades",                 tension: 0.0,  valence: 0.0 },
            { time: 38,   text: "Truth revealed",                     tension: 0.4,  valence: -0.4 },
            { time: 41,   text: "We were always falling",             tension: 0.2,  valence: -0.6 },
            { time: 44,   text: "Down",                               tension: 0.0,  valence: -0.7 },
            { time: 48,   text: "...",                                tension: -0.5, valence: -0.8 },
        ]
    }
};

// Export for use in voicepath.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DEMO_SONGS;
}
