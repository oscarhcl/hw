// Local data to be stored in localStorage (different from remote data)
const localProjectsData = [
    {
        id: 1,
        title: "Leaseflow AI - LLM-powered Rental Search Platform",
        image: "pickup1.png",
        imageAlt: "Leaseflow AI platform interface showing rental search with AI chat assistant",
        description: "Built and deployed a full-stack rental search platform with an LLM-powered chat assistant, designing and containerizing 7 REST APIs (Python, Express) for listing retrieval, chat logic, and query filtering. Integrated MongoDB Atlas vector search to reduce semantic query latency by 135%.",
        technologies: "React, Node.js, Express, MongoDB, LangChain, Docker",
        date: "2024",
        link: "https://github.com",
        linkText: "View Project"
    },
    {
        id: 2,
        title: "On-campus Pickup Basketball Virtual Queuing iOS App",
        image: "pickup2.png",
        imageAlt: "Pickup Basketball app screenshot showing virtual queue interface and live game tracking",
        description: "Built a React Native iOS app for UCSD students to manage pickup basketball through virtual queues, live game tracking, and player profiles. Implemented Apple ID login and real-time Supabase sync, achieving less than 200ms update latency.",
        technologies: "React Native, Supabase, Expo, Apple ID Auth",
        date: "2024",
        link: "https://github.com",
        linkText: "View Source Code"
    }
];

// Initialize localStorage with local data if not already set
function initializeLocalStorage() {
    if (!localStorage.getItem('projects')) {
        localStorage.setItem('projects', JSON.stringify(localProjectsData));
    }
}

// Render project cards from data array
function renderProjectCards(projects) {
    const container = document.getElementById('cards-container');
    container.innerHTML = ''; // Clear existing cards

    projects.forEach(project => {
        const card = document.createElement('project-card');
        card.setAttribute('title', project.title);
        card.setAttribute('image', project.image);
        card.setAttribute('image-alt', project.imageAlt || project.imageAlt || 'Project image');
        card.setAttribute('description', project.description);

        if (project.technologies) {
            card.setAttribute('technologies', project.technologies);
        }
        if (project.date) {
            card.setAttribute('date', project.date);
        }
        if (project.link) {
            card.setAttribute('link', project.link);
        }
        if (project.linkText) {
            card.setAttribute('link-text', project.linkText);
        }

        container.appendChild(card);
    });
}

// Load projects from localStorage
function loadLocalProjects() {
    try {
        const data = localStorage.getItem('projects');
        if (data) {
            const projects = JSON.parse(data);
            renderProjectCards(projects);
            console.log('Loaded projects from localStorage:', projects);
        } else {
            console.log('No projects found in localStorage');
            alert('No local data found. Initializing with default data...');
            initializeLocalStorage();
            loadLocalProjects();
        }
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        alert('Error loading local data: ' + error.message);
    }
}

// Load projects from remote server (My JSON Server)
// Replace YOUR_GITHUB_USERNAME with your actual GitHub username after pushing db.json
async function loadRemoteProjects() {
    // Using My JSON Server - it uses your GitHub repo as a fake REST API
    // Format: https://my-json-server.typicode.com/{github-username}/{repo-name}/projects
    const remoteUrl = 'https://my-json-server.typicode.com/oscarhhung/cse134-hw5/projects';

    try {
        const response = await fetch(remoteUrl);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const projects = await response.json();

        // Map the remote data format to match our card attributes
        const mappedProjects = projects.map(project => ({
            title: project.title,
            image: project.image,
            imageAlt: project.imageAlt,
            description: project.description,
            technologies: project.technologies || '',
            date: project.date || '',
            link: project.link || 'https://github.com',
            linkText: project.linkText || 'Learn More'
        }));

        renderProjectCards(mappedProjects);
        console.log('Loaded projects from remote:', mappedProjects);
    } catch (error) {
        console.error('Error loading from remote:', error);
        alert('Error loading remote data: ' + error.message + '\n\nMake sure your GitHub repo has db.json in the root directory.');
    }
}

// Event delegation for button clicks
document.addEventListener('DOMContentLoaded', () => {
    // Initialize localStorage
    initializeLocalStorage();

    // Add event listeners using event delegation on button container
    const buttonContainer = document.querySelector('.button-container');

    if (buttonContainer) {
        buttonContainer.addEventListener('click', (event) => {
            const target = event.target;

            if (target.id === 'load-local-btn') {
                loadLocalProjects();
            } else if (target.id === 'load-remote-btn') {
                loadRemoteProjects();
            }
        });
    }
});
