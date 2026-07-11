/* ================================================================
   DEVELOPER PROFILES  --  Meet the team behind GreySignal
   ================================================================ */

const TEAM = [
  {
    name: 'Ritabrata Paul',
    role: 'Full-Stack & Deployment',
    initials: 'RP',
    gradient: 'linear-gradient(145deg, #22D3EE, #0891B2)',
    website: 'https://ritabratapaul.vercel.app/',
    github: 'https://github.com/Ritabrata-Paul',
    githubLabel: 'Ritabrata-Paul',
    linkedin: 'https://www.linkedin.com/in/ritabrata-paul-23a75919a',
    email: 'ritabrata720@gmail.com',
  },
  {
    name: 'Arnab Mondal',
    role: 'Backend & ML Engineering',
    initials: 'AM',
    gradient: 'linear-gradient(145deg, #F5B942, #F97316)',
    website: null,
    github: 'https://github.com/Ar9ab007cpu',
    githubLabel: 'Ar9ab007cpu',
    linkedin: 'https://www.linkedin.com/in/arnab-mondal-a511b822a/',
    email: 'arnabm2502@gmail.com',
  },
  {
    name: 'Arpan Chakraborty',
    role: 'Frontend & Product',
    initials: 'AC',
    gradient: 'linear-gradient(145deg, #A78BFA, #7C3AED)',
    website: null,
    github: 'https://github.com/ARPAN76',
    githubLabel: 'ARPAN76',
    linkedin: 'https://www.linkedin.com/in/arpan97',
    email: 'chakrabartyarpan17@gmail.com',
  },
  {
    name: 'Srija Biswas',
    role: 'Data & Research',
    initials: 'SB',
    gradient: 'linear-gradient(145deg, #34D399, #059669)',
    website: null,
    github: 'https://github.com/srijabiswas-01',
    githubLabel: 'srijabiswas-01',
    linkedin: 'https://www.linkedin.com/in/srija-biswas-a378561a6/',
    email: 'srijabiswas3001@gmail.com',
  },
];

function GithubIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
      <path d="M12 .5C5.37.5 0 5.87 0 12.5c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.2.09 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.34-5.47-5.95 0-1.31.47-2.39 1.24-3.23-.13-.31-.54-1.53.12-3.19 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.25 2.88.12 3.19.77.84 1.24 1.92 1.24 3.23 0 4.62-2.81 5.64-5.49 5.94.43.37.81 1.1.81 2.22v3.29c0 .32.22.7.83.58A12.01 12.01 0 0 0 24 12.5C24 5.87 18.63.5 12 .5Z" />
    </svg>
  );
}

function LinkedinIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
      <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29ZM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14ZM7.12 20.45H3.56V9h3.56v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0Z" />
    </svg>
  );
}

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-10 6L2 7" />
    </svg>
  );
}

function GlobeIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  );
}

function DeveloperCard({ member }) {
  return (
    <div className="dev-card">
      <div className="dev-card-top">
        <div className="dev-avatar" style={{ background: member.gradient }}>
          {member.initials}
        </div>
        <div className="dev-identity">
          <h4 className="dev-name">{member.name}</h4>
          <span className="dev-role">{member.role}</span>
        </div>
      </div>

      <div className="dev-links">
        {member.website && (
          <a className="dev-link" href={member.website} target="_blank" rel="noreferrer" title="Portfolio website">
            <GlobeIcon />
            <span>Portfolio</span>
          </a>
        )}
        <a className="dev-link" href={member.github} target="_blank" rel="noreferrer" title={`GitHub: ${member.githubLabel}`}>
          <GithubIcon />
          <span>{member.githubLabel}</span>
        </a>
        <a className="dev-link" href={member.linkedin} target="_blank" rel="noreferrer" title="LinkedIn profile">
          <LinkedinIcon />
          <span>LinkedIn</span>
        </a>
        {member.email && (
          <a className="dev-link" href={`mailto:${member.email}`} title={`Email: ${member.email}`}>
            <MailIcon />
            <span>{member.email}</span>
          </a>
        )}
      </div>
    </div>
  );
}

export default function Developers() {
  return (
    <div className="dev-page">
      <div className="dev-hero">
        <span className="dev-hero-eyebrow">The Team</span>
        <h1 className="dev-hero-title">Meet the Developers</h1>
        <p className="dev-hero-sub">
          GreySignal was designed and built by a small team for the Hackathon 2026 —
          combining backend, machine learning, frontend, and data research into one
          geopolitical risk intelligence platform.
        </p>
      </div>

      <div className="dev-grid">
        {TEAM.map((member) => (
          <DeveloperCard key={member.name} member={member} />
        ))}
      </div>

      <div className="dev-footnote">
        Interested in the code? Explore the project on{' '}
        <a href="https://github.com/Ar9ab007cpu/GreySignal-hackathon-2026" target="_blank" rel="noreferrer">
          GitHub
        </a>
        .
      </div>
    </div>
  );
}
