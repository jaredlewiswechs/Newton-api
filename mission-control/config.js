/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON MISSION CONTROL - API ENDPOINT CONFIGURATION
 * Single source of truth for all Newton API endpoints
 * 
 * © 2026 Jared Lewis · Ada Computing Company
 * Updated: February 2026
 * ═══════════════════════════════════════════════════════════════════════════
 */

// Helper to detect API base URL
function getApiBase() {
    const hostname = window.location.hostname;
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // Vercel deployment - API is on same origin (PRIMARY)
    if (hostname.endsWith('.vercel.app') || hostname === 'vercel.app') {
        return window.location.origin;
    }
    
    // Legacy Render deployment - API is on same origin
    if (hostname.endsWith('.onrender.com') || hostname === 'onrender.com') {
        return window.location.origin;
    }
    
    // Cloudflare Pages or other static hosting - same origin
    if (hostname.endsWith('.pages.dev') || hostname === 'pages.dev' ||
        hostname.endsWith('.cloudflare.com') || hostname === 'cloudflare.com') {
        return window.location.origin;
    }
    
    // Default: assume API is on same origin
    return window.location.origin;
}

export const API_ENVIRONMENTS = {
    localhost: 'http://localhost:8000',
    production: getApiBase(),
    custom: '' // User can set custom URL
};

export const ENDPOINTS = {
    core: {
        name: 'Core Verification',
        description: 'Fundamental verification and computation',
        endpoints: [
            {
                path: '/ask',
                method: 'POST',
                name: 'Ask Newton',
                description: 'Full verification pipeline - ask a question',
                sampleData: { query: "What is 2+2?" }
            },
            {
                path: '/verify',
                method: 'POST',
                name: 'Verify Content',
                description: 'Verify content against constraints',
                sampleData: { input: "Test content", constraints: [] }
            },
            {
                path: '/verify/batch',
                method: 'POST',
                name: 'Batch Verify',
                description: 'Verify multiple items at once',
                sampleData: { inputs: ["item1", "item2"] }
            },
            {
                path: '/calculate',
                method: 'POST',
                name: 'Calculate',
                description: 'Verified computation with bounded execution',
                sampleData: { expression: { "op": "+", "args": [2, 2] } }
            },
            {
                path: '/calculate/examples',
                method: 'POST',
                name: 'Calculate Examples',
                description: 'Get example expressions',
                sampleData: {}
            },
            {
                path: '/constraint',
                method: 'POST',
                name: 'Constraint Check',
                description: 'Evaluate CDL constraints',
                sampleData: { 
                    constraint: { "op": "gt", "field": "value", "value": 0 },
                    object: { value: 5 }
                }
            }
        ]
    },

    education: {
        name: 'Education',
        description: 'TEKS-aligned lesson planning and assessment',
        endpoints: [
            {
                path: '/education/teks',
                method: 'GET',
                name: 'TEKS Standards',
                description: 'Get all TEKS standards'
            },
            {
                path: '/education/teks/5.3A',
                method: 'GET',
                name: 'TEKS by Code',
                description: 'Get specific TEKS standard (example: 5.3A)'
            },
            {
                path: '/education/teks/search',
                method: 'POST',
                name: 'Search TEKS',
                description: 'Search TEKS standards',
                sampleData: { query: "multiplication" }
            },
            {
                path: '/education/lesson',
                method: 'POST',
                name: 'Generate Lesson',
                description: 'Generate TEKS-aligned lesson plan',
                sampleData: { 
                    grade: 5,
                    subject: "Math",
                    teks_codes: ["5.3A"],
                    topic: "Multiplication strategies",
                    student_needs: {
                        ell: ["visual_aids", "sentence_frames"]
                    }
                }
            },
            {
                path: '/education/slides',
                method: 'POST',
                name: 'Generate Slides',
                description: 'Generate presentation slides',
                sampleData: {
                    lesson_plan: {
                        title: "Multiplication Models",
                        grade: 5,
                        subject: "Math",
                        teks_alignment: [{"code": "5.3A"}],
                        objective: "Model multiplication with arrays",
                        phases: [
                            {
                                "phase": "instruction",
                                "title": "Mini Lesson",
                                "duration_minutes": 15,
                                "activities": ["Model arrays on grid paper"]
                            }
                        ],
                        assessment: {"exit_ticket": "Draw an array for 4 x 6"}
                    },
                    style: "modern"
                }
            },
            {
                path: '/education/assess',
                method: 'POST',
                name: 'Assessment Analysis',
                description: 'Analyze assessment scores',
                sampleData: { 
                    assessment_name: "Unit 1 Check",
                    teks_codes: ["5.3A"],
                    total_points: 10,
                    mastery_threshold: 80,
                    students: [
                        {"id": "S1", "name": "Ava", "score": 9},
                        {"id": "S2", "name": "Liam", "score": 7}
                    ]
                }
            },
            {
                path: '/education/plc',
                method: 'POST',
                name: 'PLC Report',
                description: 'Generate Professional Learning Community report',
                sampleData: {
                    assessment_data: [
                        {"id": "S1", "name": "Ava", "score": 9},
                        {"id": "S2", "name": "Liam", "score": 7}
                    ],
                    teks_codes: ["5.3A"],
                    team_name: "Grade 5 Math"
                }
            },
            {
                path: '/education/info',
                method: 'GET',
                name: 'Education Info',
                description: 'Get education module information'
            }
        ]
    },

    teachers: {
        name: "Teacher's Aide",
        description: 'Student tracking and classroom management',
        endpoints: [
            {
                path: '/teachers/db',
                method: 'GET',
                name: 'Database Info',
                description: 'Get database statistics'
            },
            {
                path: '/teachers/students',
                method: 'POST',
                name: 'Add Student',
                description: 'Add a student to the database',
                sampleData: {
                    first_name: "John",
                    last_name: "Doe",
                    grade: 5,
                    student_id: "S12345",
                    accommodations: ["ell"]
                }
            },
            {
                path: '/teachers/students',
                method: 'GET',
                name: 'List Students',
                description: 'Get all students'
            },
            {
                path: '/teachers/classrooms',
                method: 'POST',
                name: 'Create Classroom',
                description: 'Create a new classroom',
                sampleData: {
                    name: "Math Period 1",
                    grade: 5,
                    subject: "Math"
                }
            },
            {
                path: '/teachers/classrooms',
                method: 'GET',
                name: 'List Classrooms',
                description: 'Get all classrooms'
            },
            {
                path: '/teachers/assessments',
                method: 'POST',
                name: 'Create Assessment',
                description: 'Create a new assessment',
                sampleData: {
                    name: "Unit 1 Test",
                    classroom_id: "CLASS001",
                    teks_codes: ["5.3A", "5.3B"],
                    total_points: 100
                }
            },
            {
                path: '/teachers/assessments',
                method: 'GET',
                name: 'List Assessments',
                description: 'Get all assessments'
            },
            {
                path: '/teachers/interventions',
                method: 'POST',
                name: 'Create Intervention',
                description: 'Create intervention plan',
                sampleData: {
                    classroom_id: "CLASS001",
                    teks_codes: ["5.3A"],
                    target_group: "needs_reteach",
                    strategy: "Small group instruction"
                }
            },
            {
                path: '/teachers/interventions',
                method: 'GET',
                name: 'List Interventions',
                description: 'Get all intervention plans'
            },
            {
                path: '/teachers/teks',
                method: 'GET',
                name: 'Teacher TEKS',
                description: 'Get TEKS for teachers'
            },
            {
                path: '/teachers/teks/stats',
                method: 'GET',
                name: 'TEKS Statistics',
                description: 'Get TEKS usage statistics'
            },
            {
                path: '/teachers/info',
                method: 'GET',
                name: "Teacher's Aide Info",
                description: "Get Teacher's Aide information"
            }
        ]
    },

    grounding: {
        name: 'Grounding',
        description: 'Ground claims in external evidence',
        endpoints: [
            {
                path: '/ground',
                method: 'POST',
                name: 'Ground Claim',
                description: 'Ground a claim in verifiable evidence',
                sampleData: {
                    claim: "Paris is the capital of France"
                }
            }
        ]
    },

    statistics: {
        name: 'Statistics',
        description: 'Robust adversarial statistics',
        endpoints: [
            {
                path: '/statistics',
                method: 'POST',
                name: 'Robust Statistics',
                description: 'Calculate adversarial-resistant statistics',
                sampleData: {
                    values: [1, 2, 3, 4, 5, 100],
                    method: "mad"
                }
            }
        ]
    },

    jester: {
        name: 'Jester',
        description: 'Code constraint analyzer',
        endpoints: [
            {
                path: '/jester/analyze',
                method: 'POST',
                name: 'Analyze Code',
                description: 'Extract constraints from code',
                sampleData: {
                    code: "if x > 0: return x * 2",
                    language: "python"
                }
            },
            {
                path: '/jester/cdl',
                method: 'POST',
                name: 'Convert to CDL',
                description: 'Convert code constraints to CDL',
                sampleData: {
                    code: "assert x > 0",
                    language: "python"
                }
            },
            {
                path: '/jester/info',
                method: 'GET',
                name: 'Jester Info',
                description: 'Get Jester information'
            },
            {
                path: '/jester/languages',
                method: 'GET',
                name: 'Supported Languages',
                description: 'Get supported programming languages'
            },
            {
                path: '/jester/constraint-kinds',
                method: 'GET',
                name: 'Constraint Kinds',
                description: 'Get supported constraint types'
            }
        ]
    },

    interface: {
        name: 'Interface Builder',
        description: 'Build user interfaces from descriptions',
        endpoints: [
            {
                path: '/interface/templates',
                method: 'GET',
                name: 'List Templates',
                description: 'Get all interface templates'
            },
            {
                path: '/interface/build',
                method: 'POST',
                name: 'Build Interface',
                description: 'Generate interface from description',
                sampleData: {
                    template_id: "dashboard-basic",
                    variables: {
                        title: "Mission Control",
                        metric1_value: "99.8%",
                        metric1_label: "Uptime"
                    },
                    output_format: "json"
                }
            },
            {
                path: '/interface/components',
                method: 'GET',
                name: 'List Components',
                description: 'Get available UI components'
            },
            {
                path: '/interface/info',
                method: 'GET',
                name: 'Interface Builder Info',
                description: 'Get Interface Builder information'
            }
        ]
    },

    glassbox: {
        name: 'Glass Box',
        description: 'Transparency and governance',
        endpoints: [
            {
                path: '/merkle/anchors',
                method: 'GET',
                name: 'Merkle Anchors',
                description: 'Get all Merkle anchors'
            },
            {
                path: '/merkle/anchor',
                method: 'POST',
                name: 'Create Anchor',
                description: 'Create a new Merkle anchor',
                sampleData: {
                    data: "anchor data"
                }
            },
            {
                path: '/merkle/latest',
                method: 'GET',
                name: 'Latest Anchor',
                description: 'Get latest Merkle anchor'
            },
            {
                path: '/negotiator/pending',
                method: 'GET',
                name: 'Pending Requests',
                description: 'Get pending negotiator requests'
            },
            {
                path: '/negotiator/request',
                method: 'POST',
                name: 'Create Request',
                description: 'Create negotiator request',
                sampleData: {
                    operation: "content_publish",
                    input_data: "Publish daily summary report",
                    reason: "Requires human approval",
                    priority: "medium"
                }
            },
            {
                path: '/policy',
                method: 'GET',
                name: 'List Policies',
                description: 'Get all policies'
            },
            {
                path: '/policy',
                method: 'POST',
                name: 'Create Policy',
                description: 'Create a new policy',
                sampleData: {
                    id: "policy-001",
                    name: "Max Payload Size",
                    type: "size_limit",
                    action: "deny",
                    condition: {"max_length": 5000}
                }
            }
        ]
    },

    ledger: {
        name: 'Ledger',
        description: 'Immutable audit trail',
        endpoints: [
            {
                path: '/ledger',
                method: 'GET',
                name: 'View Ledger',
                description: 'Get ledger entries'
            },
            {
                path: '/ledger/1',
                method: 'GET',
                name: 'Get Entry',
                description: 'Get ledger entry with Merkle proof (example: index 1)'
            },
            {
                path: '/ledger/certificate/1',
                method: 'GET',
                name: 'Export Certificate',
                description: 'Export verification certificate (example: index 1)'
            }
        ]
    },

    vault: {
        name: 'Vault',
        description: 'Encrypted storage',
        endpoints: [
            {
                path: '/vault/store',
                method: 'POST',
                name: 'Store Data',
                description: 'Store encrypted data',
                sampleData: {
                    key: "tester",
                    identity: "tester",
                    passphrase: "tester",
                    data: {
                        message: "sensitive data"
                    }
                }
            },
            {
                path: '/vault/retrieve',
                method: 'POST',
                name: 'Retrieve Data',
                description: 'Retrieve encrypted data',
                sampleData: {
                    key: "tester",
                    identity: "tester",
                    passphrase: "tester",
                    entry_id: "V_TEST_ENTRY"
                }
            }
        ]
    },

    chatbot: {
        name: 'Chatbot Compiler',
        description: 'Better ChatGPT with governance',
        endpoints: [
            {
                path: '/chatbot/compile',
                method: 'POST',
                name: 'Compile Request',
                description: 'Compile and validate chatbot request',
                sampleData: {
                    input: "Tell me about the weather"
                }
            },
            {
                path: '/chatbot/classify',
                method: 'POST',
                name: 'Classify Request',
                description: 'Classify request type and risk',
                sampleData: {
                    input: "What is 2+2?"
                }
            },
            {
                path: '/chatbot/batch',
                method: 'POST',
                name: 'Batch Compile',
                description: 'Compile multiple requests',
                sampleData: {
                    inputs: ["Hello", "How are you?"]
                }
            },
            {
                path: '/chatbot/metrics',
                method: 'GET',
                name: 'Metrics',
                description: 'Get chatbot metrics'
            },
            {
                path: '/chatbot/types',
                method: 'GET',
                name: 'Request Types',
                description: 'Get supported request types'
            },
            {
                path: '/chatbot/example',
                method: 'GET',
                name: 'Example',
                description: 'Get example chatbot request'
            }
        ]
    },

    voice: {
        name: 'Voice Interface',
        description: 'Voice commands and streaming (MOAD)',
        endpoints: [
            {
                path: '/voice/ask',
                method: 'POST',
                name: 'Voice Ask',
                description: 'Process voice query',
                sampleData: {
                    query: "What is the weather?"
                }
            },
            {
                path: '/voice/stream',
                method: 'POST',
                name: 'Voice Stream',
                description: 'Stream voice response',
                sampleData: {
                    query: "Tell me a story"
                }
            },
            {
                path: '/voice/intent',
                method: 'POST',
                name: 'Parse Intent',
                description: 'Parse user intent from voice',
                sampleData: {
                    text: "Set timer for 5 minutes"
                }
            },
            {
                path: '/voice/patterns',
                method: 'GET',
                name: 'Voice Patterns',
                description: 'Get voice command patterns'
            },
            {
                path: '/voice/demo',
                method: 'GET',
                name: 'Voice Demo',
                description: 'Get voice interface demo'
            }
        ]
    },

    extract: {
        name: 'Constraint Extractor',
        description: 'From fuzzy to formal constraints',
        endpoints: [
            {
                path: '/extract',
                method: 'POST',
                name: 'Extract Constraints',
                description: 'Extract formal constraints from text',
                sampleData: {
                    text: "The price must be greater than 0 and less than 100"
                }
            },
            {
                path: '/extract/verify',
                method: 'POST',
                name: 'Verify Plan',
                description: 'Verify extracted constraints',
                sampleData: {
                    plan: {
                        name: "Sample Plan",
                        group_size: 2,
                        duration_week: 1
                    },
                    text: "A trip for two friends lasting one week."
                }
            },
            {
                path: '/extract/example',
                method: 'GET',
                name: 'Extract Example',
                description: 'Get constraint extraction example'
            }
        ]
    },

    cartridges: {
        name: 'Cartridges',
        description: 'Specialized computation modules',
        endpoints: [
            {
                path: '/cartridge/visual',
                method: 'POST',
                name: 'Visual Cartridge',
                description: 'Visual computation',
                sampleData: { intent: "Generate a bar chart for quarterly sales" }
            },
            {
                path: '/cartridge/sound',
                method: 'POST',
                name: 'Sound Cartridge',
                description: 'Audio computation',
                sampleData: { intent: "Create a calming notification chime" }
            },
            {
                path: '/cartridge/sequence',
                method: 'POST',
                name: 'Sequence Cartridge',
                description: 'Sequence analysis',
                sampleData: { intent: "Storyboard a 10-second intro animation" }
            },
            {
                path: '/cartridge/data',
                method: 'POST',
                name: 'Data Cartridge',
                description: 'Data processing',
                sampleData: { intent: "Summarize weekly metrics", data: { visits: 1200 } }
            },
            {
                path: '/cartridge/rosetta',
                method: 'POST',
                name: 'Rosetta Cartridge',
                description: 'Translation',
                sampleData: { intent: "Create a Swift function that validates an email" }
            },
            {
                path: '/cartridge/auto',
                method: 'POST',
                name: 'Auto Cartridge',
                description: 'Auto-select cartridge',
                sampleData: { intent: "Generate a report summary for Q1" }
            },
            {
                path: '/cartridge/info',
                method: 'GET',
                name: 'Cartridge Info',
                description: 'Get cartridge information'
            }
        ]
    },

    gumroad: {
        name: 'Gumroad',
        description: 'License management and payments',
        endpoints: [
            {
                path: '/license/verify',
                method: 'POST',
                name: 'Verify License',
                description: 'Verify Gumroad license',
                sampleData: {
                    license_key: "TEST_LICENSE"
                }
            },
            {
                path: '/license/info',
                method: 'GET',
                name: 'License Info',
                description: 'Get license information'
            },
            {
                path: '/gumroad/stats',
                method: 'GET',
                name: 'Gumroad Stats',
                description: 'Get Gumroad statistics'
            }
        ]
    },

    parccloud: {
        name: 'parcCloud Auth',
        description: 'Authentication gateway',
        endpoints: [
            {
                path: '/parccloud/signup',
                method: 'POST',
                name: 'Sign Up',
                description: 'Create new account',
                sampleData: {
                    name: "Test User",
                    email: "tester@example.com",
                    password: "testpass123"
                }
            },
            {
                path: '/parccloud/signin',
                method: 'POST',
                name: 'Sign In',
                description: 'Sign in to account',
                sampleData: {
                    email: "tester@example.com",
                    password: "testpass123"
                }
            },
            {
                path: '/parccloud/verify',
                method: 'GET',
                name: 'Verify Token',
                description: 'Verify authentication token'
            },
            {
                path: '/parccloud/logout',
                method: 'POST',
                name: 'Logout',
                description: 'Logout user',
                sampleData: {
                    token: "example-token"
                }
            },
            {
                path: '/parccloud/stats',
                method: 'GET',
                name: 'User Stats',
                description: 'Get user statistics'
            }
        ]
    },

    system: {
        name: 'System',
        description: 'Health and diagnostics',
        endpoints: [
            {
                path: '/health',
                method: 'GET',
                name: 'Health Check',
                description: 'System health status'
            },
            {
                path: '/metrics',
                method: 'GET',
                name: 'Metrics',
                description: 'Performance metrics'
            },
            {
                path: '/openapi.json',
                method: 'GET',
                name: 'OpenAPI Spec',
                description: 'API specification'
            },
            {
                path: '/feedback',
                method: 'POST',
                name: 'Send Feedback',
                description: 'Submit user feedback',
                sampleData: {
                    message: "Great API!",
                    rating: 5
                }
            },
            {
                path: '/feedback/summary',
                method: 'GET',
                name: 'Feedback Summary',
                description: 'Get feedback summary'
            }
        ]
    }
};

// Default configuration
export const DEFAULT_CONFIG = {
    environment: 'localhost',
    customUrl: '',
    timeout: 30000,
    autoRefresh: true,
    refreshInterval: 30,
    theme: 'dark'
};
