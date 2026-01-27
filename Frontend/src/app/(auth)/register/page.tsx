// src/app/register/page.tsx
'use client'

import { Navbar } from '@/components/layout/navbar'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Eye, 
  EyeOff, 
  ArrowRight, 
  CheckCircle2,
  AlertCircle,
  User,
  Mail,
  Lock,
  Building2,
  Link
} from 'lucide-react'
import { useState } from 'react'

export default
function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    password: '',
    confirmPassword: ''
  })
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const [agreedToMarketing, setAgreedToMarketing] = useState(false)
  const [error, setError] = useState('')
  const [passwordStrength, setPasswordStrength] = useState(0)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

    // Calculate password strength
    if (name === 'password') {
      let strength = 0
      if (value.length >= 8) strength++
      if (value.match(/[a-z]/) && value.match(/[A-Z]/)) strength++
      if (value.match(/[0-9]/)) strength++
      if (value.match(/[^a-zA-Z0-9]/)) strength++
      setPasswordStrength(strength)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (!agreedToTerms) {
      setError('You must agree to the Terms of Service')
      return
    }

    // Add your registration logic here
    console.log({ ...formData, agreedToTerms, agreedToMarketing })
  }

  const getPasswordStrengthColor = () => {
    if (passwordStrength === 0) return 'bg-muted'
    if (passwordStrength === 1) return 'bg-red-500'
    if (passwordStrength === 2) return 'bg-yellow-500'
    if (passwordStrength === 3) return 'bg-blue-500'
    return 'bg-green-500'
  }

  const getPasswordStrengthText = () => {
    if (passwordStrength === 0) return 'Enter password'
    if (passwordStrength === 1) return 'Weak'
    if (passwordStrength === 2) return 'Fair'
    if (passwordStrength === 3) return 'Good'
    return 'Strong'
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-foreground bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]">
        <Navbar />
      {/* Split Layout */}
      <div className="min-h-screen grid lg:grid-cols-2">

        {/* LEFT: Registration Form */}
        <div className="flex items-center justify-center p-6 md:p-12 order-2 lg:order-1">
          <div className="w-full max-w-md space-y-8">

            {/* Mobile Logo */}
            <div className="lg:hidden flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-foreground border-2 border-foreground" />
              <div>
                <h1 className="text-xl font-black uppercase tracking-tighter">FinanceHub</h1>
                <p className="text-[10px] font-mono opacity-60">TERMINAL_V4.2.1</p>
              </div>
            </div>

            {/* Header */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="rounded-none border-2 border-foreground font-mono text-[10px]">
                  NEW_ACCOUNT
                </Badge>
              </div>
              <h2 className="text-4xl font-black uppercase tracking-tighter">
                Create <br />Account
              </h2>
              <p className="text-sm text-muted-foreground font-mono">
                Join 50,000+ professional traders
              </p>
            </div>

            {/* Error Alert */}
            {error && (
              <Alert className="brutalist-glass bg-red-500/10 border-red-500 text-red-600 dark:text-red-400 rounded-none">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="font-mono text-xs">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            {/* Registration Form */}
            <form onSubmit={handleSubmit} className="brutalist-glass p-8 space-y-6">

              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName" className="text-xs font-black uppercase tracking-wider">
                    First Name
                  </Label>
                  <Input
                    id="firstName"
                    name="firstName"
                    type="text"
                    placeholder="John"
                    value={formData.firstName}
                    onChange={handleChange}
                    className="brutalist-input h-12 rounded-none font-mono"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName" className="text-xs font-black uppercase tracking-wider">
                    Last Name
                  </Label>
                  <Input
                    id="lastName"
                    name="lastName"
                    type="text"
                    placeholder="Doe"
                    value={formData.lastName}
                    onChange={handleChange}
                    className="brutalist-input h-12 rounded-none font-mono"
                    required
                  />
                </div>
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email" className="text-xs font-black uppercase tracking-wider">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="trader@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    className="brutalist-input h-12 rounded-none font-mono pl-12"
                    required
                  />
                </div>
              </div>

              {/* Company Field (Optional) */}
              <div className="space-y-2">
                <Label htmlFor="company" className="text-xs font-black uppercase tracking-wider">
                  Company <span className="text-muted-foreground font-normal">(Optional)</span>
                </Label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="company"
                    name="company"
                    type="text"
                    placeholder="Acme Trading LLC"
                    value={formData.company}
                    onChange={handleChange}
                    className="brutalist-input h-12 rounded-none font-mono pl-12"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-xs font-black uppercase tracking-wider">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••••••"
                    value={formData.password}
                    onChange={handleChange}
                    className="brutalist-input h-12 rounded-none font-mono pl-12 pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>

                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="space-y-2">
                    <div className="flex gap-1">
                      {[...Array(4)].map((_, i) => (
                        <div
                          key={i}
                          className={`h-1 flex-1 border border-foreground transition-colors ${
                            i < passwordStrength ? getPasswordStrengthColor() : 'bg-muted'
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-xs font-mono font-bold">
                      Strength: {getPasswordStrengthText()}
                    </p>
                  </div>
                )}
              </div>

              {/* Confirm Password Field */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-xs font-black uppercase tracking-wider">
                  Confirm Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="••••••••••••"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="brutalist-input h-12 rounded-none font-mono pl-12 pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {/* Terms & Conditions */}
              <div className="space-y-3 pt-2">
                <div className="flex items-start space-x-3">
                  <Checkbox 
                    id="terms" 
                    checked={agreedToTerms}
                    onCheckedChange={(checked) => setAgreedToTerms(checked as boolean)}
                    className="rounded-none border-2 border-foreground mt-1"
                  />
                  <Label 
                    htmlFor="terms" 
                    className="text-xs leading-relaxed cursor-pointer"
                  >
                    I agree to the{' '}
                    <Link href="/terms" className="font-bold text-primary hover:underline">
                      Terms of Service
                    </Link>
                    {' '}and{' '}
                    <Link href="/privacy" className="font-bold text-primary hover:underline">
                      Privacy Policy
                    </Link>
                  </Label>
                </div>

                <div className="flex items-start space-x-3">
                  <Checkbox 
                    id="marketing" 
                    checked={agreedToMarketing}
                    onCheckedChange={(checked) => setAgreedToMarketing(checked as boolean)}
                    className="rounded-none border-2 border-foreground mt-1"
                  />
                  <Label 
                    htmlFor="marketing" 
                    className="text-xs leading-relaxed cursor-pointer text-muted-foreground"
                  >
                    Send me market insights and product updates
                  </Label>
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="brutalist-interactive w-full h-14 rounded-none border-4 border-foreground bg-foreground text-background font-black text-lg uppercase tracking-tighter hover:bg-primary hover:border-primary shadow-[6px_6px_0px_0px_var(--foreground)] hover:shadow-[6px_6px_0px_0px_var(--primary)]"
              >
                Create Account
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t-2 border-foreground/20" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground font-black">
                    Or sign up with
                  </span>
                </div>
              </div>

              {/* Social Sign Up */}
              <div className="grid grid-cols-2 gap-4">
                <Button
                  type="button"
                  variant="outline"
                  className="brutalist-interactive h-12 rounded-none border-2 border-foreground font-black uppercase text-xs"
                >
                  Google
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="brutalist-interactive h-12 rounded-none border-2 border-foreground font-black uppercase text-xs"
                >
                  GitHub
                </Button>
              </div>
            </form>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                Already have an account?{' '}
                <Link 
                  href="/login" 
                  className="font-black text-primary hover:underline uppercase"
                >
                  Sign In →
                </Link>
              </p>
            </div>

            {/* Footer */}
            <div className="text-center pt-8">
              <p className="text-xs text-muted-foreground font-mono">
                Protected by 256-bit SSL encryption
              </p>
            </div>
          </div>
        </div>

        {/* RIGHT: Benefits & Social Proof */}
        <div className="hidden lg:flex flex-col justify-between p-12 bg-foreground text-background relative overflow-hidden order-1 lg:order-2">
          {/* Decorative Elements */}
          <div className="absolute top-0 left-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />

          <div className="relative z-10">
            {/* Logo */}
            <div className="flex items-center gap-3 mb-16">
              <div className="w-12 h-12 bg-primary border-4 border-background" />
              <div>
                <h1 className="text-2xl font-black uppercase tracking-tighter">FinanceHub</h1>
                <p className="text-xs font-mono opacity-60">TERMINAL_V4.2.1</p>
              </div>
            </div>

            {/* Benefits */}
            <div className="space-y-8 max-w-md">
              <h2 className="text-5xl font-black uppercase tracking-tighter leading-[0.9]">
                Start Trading <br />
                Like a <br />
                <span className="text-primary">Professional.</span>
              </h2>

              <p className="text-lg opacity-80 font-mono">
                Join thousands of traders using institutional-grade tools.
              </p>

              <div className="space-y-6 pt-8">
                <div className="flex items-start gap-4">
                  <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-black uppercase text-sm mb-1">Free 30-Day Trial</h3>
                    <p className="text-sm opacity-70">Full access to all premium features, no credit card required</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-black uppercase text-sm mb-1">Advanced Analytics</h3>
                    <p className="text-sm opacity-70">AI-powered insights and real-time market analysis</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-black uppercase text-sm mb-1">24/7 Support</h3>
                    <p className="text-sm opacity-70">Dedicated support team available around the clock</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-black uppercase text-sm mb-1">Multi-Asset Trading</h3>
                    <p className="text-sm opacity-70">Stocks, crypto, forex, and commodities in one platform</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Testimonial */}
          <div className="relative z-10 brutalist-glass-ghost border-2 border-background/20 p-6">
            <p className="text-sm italic mb-4 opacity-90">
              "FinanceHub transformed how I trade. The real-time data and execution speed are unmatched. Best platform I've used in 15 years."
            </p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary border-2 border-background flex items-center justify-center">
                <User className="w-5 h-5" />
              </div>
              <div>
                <p className="font-black text-sm">Sarah Chen</p>
                <p className="text-xs opacity-60 font-mono">QUANTITATIVE TRADER</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}