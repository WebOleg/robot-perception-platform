# web/ — World B (dashboard)

React + TypeScript (Vite) frontend. Reads from the backend API and shows live
detections with per-class counts, auto-refreshing once per second. Talks only
to the API, never to the robot.

## Develop

    npm install
    npm run dev      # http://localhost:5173

API base URL is configurable via VITE_API_URL (defaults to http://localhost:8080).
