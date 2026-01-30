'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Check, Share2, Globe, Lock, Users, Mail, Link2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ShareDialogProps {
  portfolioId: string
  portfolioName: string
  isPublic: boolean
  onVisibilityChange: (isPublic: boolean) => void
}

export default function ShareDialog({ portfolioId, portfolioName, isPublic, onVisibilityChange }: ShareDialogProps) {
  const [open, setOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [shareLink, setShareLink] = useState('')
  const [allowComments, setAllowComments] = useState(false)
  const [showContactInfo, setShowContactInfo] = useState(false)

  const generateShareLink = () => {
    const baseUrl = window.location.origin
    setShareLink(`${baseUrl}/portfolios/shared/${portfolioId}`)
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(shareLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (newOpen && !shareLink) {
      generateShareLink()
    }
    setOpen(newOpen)
  }

  const handleShareTwitter = () => {
    const text = encodeURIComponent(`Check out my portfolio "${portfolioName}" on FinanceHub!`)
    const url = encodeURIComponent(shareLink)
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank')
  }

  const handleShareLinkedIn = () => {
    const url = encodeURIComponent(shareLink)
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank')
  }

  const handleShareFacebook = () => {
    const url = encodeURIComponent(shareLink)
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank')
  }

  const handleShareEmail = () => {
    const subject = encodeURIComponent(`Check out my portfolio: ${portfolioName}`)
    const body = encodeURIComponent(`I wanted to share my portfolio "${portfolioName}" with you.\n\nView it here: ${shareLink}\n\n- Created with FinanceHub`)
    window.location.href = `mailto:?subject=${subject}&body=${body}`
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Share2 className="w-4 h-4 mr-2" />
          Share
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share Portfolio</DialogTitle>
          <DialogDescription>
            Share "{portfolioName}" with others or make it public
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="link" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="link">
              <Link2 className="w-4 h-4 mr-2" />
              Link
            </TabsTrigger>
            <TabsTrigger value="social">
              <Share2 className="w-4 h-4 mr-2" />
              Social
            </TabsTrigger>
          </TabsList>

          <TabsContent value="link" className="space-y-4">
            {/* Visibility Toggle */}
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                {isPublic ? (
                  <Globe className="w-5 h-5 text-green-500" />
                ) : (
                  <Lock className="w-5 h-5 text-muted-foreground" />
                )}
                <div>
                  <Label className="text-sm font-medium">
                    {isPublic ? 'Public Portfolio' : 'Private Portfolio'}
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    {isPublic
                      ? 'Anyone with the link can view'
                      : 'Only you can access'}
                  </p>
                </div>
              </div>
              <Switch
                checked={isPublic}
                onCheckedChange={onVisibilityChange}
              />
            </div>

            {/* Share Link */}
            <div className="space-y-2">
              <Label htmlFor="share-link">Share Link</Label>
              <div className="flex gap-2">
                <Input
                  id="share-link"
                  value={shareLink}
                  readOnly
                  className="flex-1"
                />
                <Button
                  size="icon"
                  variant="outline"
                  onClick={handleCopy}
                  className="shrink-0"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Link Options */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="allow-comments" className="text-sm">
                  Allow comments
                </Label>
                <Switch
                  id="allow-comments"
                  checked={allowComments}
                  onCheckedChange={setAllowComments}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="show-contact" className="text-sm">
                  Show contact info
                </Label>
                <Switch
                  id="show-contact"
                  checked={showContactInfo}
                  onCheckedChange={setShowContactInfo}
                />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="social" className="space-y-4">
            <div className="grid gap-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleShareTwitter}
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
                Share on X (Twitter)
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleShareLinkedIn}
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
                Share on LinkedIn
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleShareFacebook}
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
                Share on Facebook
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleShareEmail}
              >
                <Mail className="w-5 h-5 mr-2" />
                Share via Email
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
