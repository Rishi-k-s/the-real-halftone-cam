import toast, { Toaster } from 'react-hot-toast';

// Toast utility functions
export const showSuccess = (message) => {
  toast.success(message, {
    duration: 3000,
    position: 'top-center',
    style: {
      background: '#10b981',
      color: 'white',
    },
  });
};

export const showError = (message) => {
  toast.error(message, {
    duration: 4000,
    position: 'top-center',
    style: {
      background: '#ef4444',
      color: 'white',
    },
  });
};

export const showLoading = (message) => {
  return toast.loading(message, {
    position: 'top-center',
  });
};

export const dismissToast = (toastId) => {
  toast.dismiss(toastId);
};

// Toast container component
export const ToastContainer = () => {
  return (
    <Toaster
      position="top-center"
      reverseOrder={false}
      gutter={8}
      containerClassName=""
      containerStyle={{}}
      toastOptions={{
        className: '',
        duration: 3000,
        style: {
          fontSize: '14px',
          maxWidth: '90vw',
        },
      }}
    />
  );
};
