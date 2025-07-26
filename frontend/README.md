# ASCIICam Frontend

A modern React frontend for the ASCIICam offline camera and printing system.

## 🚀 Features

- **Multi-step Wizard:** Capture → Process → Print workflow
- **Real-time Processing:** Live parameter adjustment with 300ms debouncing
- **Side-by-side Comparison:** Original vs processed image view
- **Mobile Responsive:** Optimized for touch devices
- **Image Caching:** Browser cache for processed images
- **Gallery:** Paginated history of captures and processed images
- **Print Integration:** CUPS printer integration
- **Toast Notifications:** User-friendly error handling

## 🛠️ Tech Stack

- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications

## 📁 Project Structure

```
src/
├── components/
│   ├── Camera/              # Photo capture component
│   ├── ImageComparison/     # Side-by-side image viewer
│   ├── ParameterControls/   # Real-time processing controls
│   ├── PrintControls/       # Printer integration
│   ├── Gallery/             # History gallery with pagination
│   ├── StepWizard/          # Multi-step navigation
│   └── Toast/               # Notification system
├── services/
│   └── api.js               # Backend API integration
├── hooks/
│   └── useImageCache.js     # Image caching logic
└── App.jsx                  # Main application
```

## 🔧 Setup & Installation

```bash
# Navigate to frontend directory
cd /home/rishi/devmt/asciicam/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🌐 API Integration

The frontend connects to the FastAPI backend at `http://localhost:5000`

### Key API Endpoints Used:
- `POST /capture` - Capture photos
- `POST /convert` - Process images (halftone/ASCII)
- `GET /preview` - Get processed image
- `GET /printers` - List available printers
- `POST /print` - Print processed image
- `GET /history` - Get image history

## 📱 Mobile Optimization

- **Responsive Design:** Adapts to all screen sizes
- **Touch-friendly Controls:** Large buttons and sliders
- **Optimized Images:** Proper sizing for mobile displays
- **Touch Navigation:** Swipe-friendly gallery

## 🎛️ Parameter Controls

### Halftone Processing:
- **Traditional Algorithm:** Toggle for enhanced quality
- **Dot Size:** 3-20 (Fine to Coarse)
- **Dot Resolution:** 2-15 (Dense to Sparse)
- **Screen Angle:** 0-89° rotation
- **Invert:** Toggle color inversion

### ASCII Art Processing:
- **Character Width:** 40-120 characters
- **Font Size:** 6-16px for image output
- **Invert:** Toggle ASCII mapping

## 🚀 Usage Flow

1. **Capture:** Click shutter button to take photo
2. **Process:** Adjust parameters to see real-time preview
3. **Print:** Select printer and print options
4. **Gallery:** Browse history of all images

Ready for integration with your ASCIICam backend!+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
