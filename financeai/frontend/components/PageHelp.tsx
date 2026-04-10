"use client";

import { HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface PageHelpProps {
  title: string;
  description: string;
  steps: string[];
  tips?: string[];
}

export default function PageHelp({ title, description, steps, tips }: PageHelpProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" className="h-8 w-8 rounded-full">
          <HelpCircle className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5 text-blue-500" />
            {title}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">{description}</p>
          <div>
            <h4 className="text-sm font-semibold mb-2">Como usar:</h4>
            <ol className="list-decimal list-inside space-y-1">
              {steps.map((step, i) => (
                <li key={i} className="text-sm text-muted-foreground">{step}</li>
              ))}
            </ol>
          </div>
          {tips && tips.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Dicas:</h4>
              <ul className="list-disc list-inside space-y-1">
                {tips.map((tip, i) => (
                  <li key={i} className="text-sm text-muted-foreground">{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
