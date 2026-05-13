import { Eye, EyeOff } from 'lucide-react';
import { useState } from 'react';

export default function PasswordInput({
  id,
  value,
  onChange,
  placeholder,
  autoComplete,
  disabled,
  ariaInvalid,
  ariaDescribedby,
  inputRef,
}) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="relative">
      <input
        id={id}
        ref={inputRef}
        type={showPassword ? 'text' : 'password'}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        autoComplete={autoComplete}
        disabled={disabled}
        aria-invalid={ariaInvalid}
        aria-describedby={ariaDescribedby}
        className="h-11 w-full rounded-lg border border-gray-200 px-3.5 pr-10 text-sm transition-colors focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
      />
      <button
        type="button"
        onClick={() => setShowPassword((v) => !v)}
        className="absolute inset-y-0 right-3 text-gray-400 hover:text-gray-600"
        aria-label={showPassword ? 'Hide password' : 'Show password'}
      >
        {showPassword ? <EyeOff className="h-[18px] w-[18px]" /> : <Eye className="h-[18px] w-[18px]" />}
      </button>
    </div>
  );
}
