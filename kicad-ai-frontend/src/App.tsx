import { useState } from 'react'
import { Cpu, Zap, Download, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface CircuitSpec {
  node_type: string
  description?: string
  esp32_model: string
  board_size: { width_mm: number; height_mm: number }
  power: { supply_voltage: number; max_current_ma: number }
  sensors: Array<{ kind: string; count: number; mounting: string }>
  actuators: Array<{ kind: string; model?: string; count: number }>
  status_leds: Array<{ color: string; role: string }>
  clarification_questions: string[]
  assumptions_made: string[]
}

interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
  pin_assignments: Record<string, string>
  power_budget_ma: number
}

interface GeneratedFile {
  filename: string
  content: string
}

function App() {
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [spec, setSpec] = useState<CircuitSpec | null>(null)
  const [questions, setQuestions] = useState<string[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [validation, setValidation] = useState<ValidationResult | null>(null)
  const [files, setFiles] = useState<Record<string, GeneratedFile>>({})
  const [step, setStep] = useState<'input' | 'review' | 'generate'>('input')

  const handleParse = async () => {
    if (!description.trim()) {
      alert('Inserisci una descrizione del circuito')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, language: 'it' })
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        const backendMsg = (data && (data.detail || data.message)) || 'Errore parsing (API sconosciuto)'
        alert(`Errore parsing: ${backendMsg}`)
        return
      }

      setSpec(data.spec)
      setQuestions(data.questions || [])
      setSuggestions(data.suggestions || [])
      setStep('review')
    } catch (error) {
      const msg = error instanceof Error ? error.message : JSON.stringify(error)
      alert(`Errore parsing (network): ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  const handleValidate = async () => {
    if (!spec) return

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec)
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        const backendMsg = (data && (data.detail || data.message)) || 'Errore validazione (API sconosciuto)'
        alert(`Errore validazione: ${backendMsg}`)
        return
      }

      setValidation(data)
    } catch (error) {
      const msg = error instanceof Error ? error.message : JSON.stringify(error)
      alert(`Errore validazione (network): ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!spec) return

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spec, project_name: 'circuito' })
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        const backendMsg = (data && (data.detail || data.message)) || 'Errore generazione (API sconosciuto)'
        alert(`Errore generazione: ${backendMsg}`)
        return
      }

      if (!data?.success) {
        const msg = data?.message || 'Errore generazione sconosciuto'
        alert(`Errore generazione: ${msg}`)
        return
      }

      setFiles(data.files)
      setValidation(data.validation)
      setStep('generate')
    } catch (error) {
      const msg = error instanceof Error ? error.message : JSON.stringify(error)
      alert(`Errore generazione (network): ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  const downloadFile = (fileKey: string) => {
    const file = files[fileKey]
    if (!file) return

    const content = atob(file.content)
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const reset = () => {
    setDescription('')
    setSpec(null)
    setQuestions([])
    setSuggestions([])
    setValidation(null)
    setFiles({})
    setStep('input')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <header className="text-center py-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Cpu className="w-12 h-12 text-indigo-600" />
            <h1 className="text-4xl font-bold text-gray-900">KiCad AI Generator</h1>
          </div>
          <p className="text-lg text-gray-600">
            Genera schemi elettronici ESP32 da descrizioni in linguaggio naturale
          </p>
        </header>

        {step === 'input' && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Descrivi il tuo circuito</CardTitle>
              <CardDescription>
                Scrivi in italiano cosa vuoi realizzare. L'AI analizzerà la descrizione e genererà le specifiche.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Esempio: Voglio un cancello automatico con 2 servo motori e un sensore IR per rilevare gli ostacoli. Aggiungi anche LED rosso e verde per lo stato."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="min-h-32 text-base"
              />
              <Button 
                onClick={handleParse} 
                disabled={loading || !description.trim()}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Analisi in corso...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-5 w-5" />
                    Analizza con AI
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {step === 'review' && spec && (
          <div className="space-y-6">
            {questions.length > 0 && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Domande di chiarimento</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    {questions.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {suggestions.length > 0 && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertTitle>Assunzioni fatte</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    {suggestions.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Specifiche del circuito</CardTitle>
                <CardDescription>Verifica le specifiche generate dall'AI</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Tipo nodo</p>
                    <p className="text-lg font-semibold">{spec.node_type}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Microcontrollore</p>
                    <p className="text-lg font-semibold">{spec.esp32_model}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Dimensioni scheda</p>
                    <p className="text-lg font-semibold">
                      {spec.board_size.width_mm}x{spec.board_size.height_mm} mm
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Alimentazione</p>
                    <p className="text-lg font-semibold">
                      {spec.power.supply_voltage}V, {spec.power.max_current_ma}mA
                    </p>
                  </div>
                </div>

                {spec.actuators.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">Attuatori</p>
                    <div className="flex flex-wrap gap-2">
                      {spec.actuators.map((a, i) => (
                        <Badge key={i} variant="secondary">
                          {a.count}x {a.kind} {a.model && `(${a.model})`}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {spec.sensors.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">Sensori</p>
                    <div className="flex flex-wrap gap-2">
                      {spec.sensors.map((s, i) => (
                        <Badge key={i} variant="secondary">
                          {s.count}x {s.kind}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {spec.status_leds.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">LED di stato</p>
                    <div className="flex flex-wrap gap-2">
                      {spec.status_leds.map((led, i) => (
                        <Badge key={i} variant="outline">
                          LED {led.color}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <Button onClick={handleValidate} disabled={loading} className="flex-1">
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Validazione...
                      </>
                    ) : (
                      'Valida circuito'
                    )}
                  </Button>
                  <Button onClick={reset} variant="outline">
                    Ricomincia
                  </Button>
                </div>
              </CardContent>
            </Card>

            {validation && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {validation.valid ? (
                      <>
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                        Validazione superata
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-5 w-5 text-red-600" />
                        Validazione fallita
                      </>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {validation.errors.length > 0 && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Errori</AlertTitle>
                      <AlertDescription>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          {validation.errors.map((e, i) => (
                            <li key={i}>{e}</li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}

                  {validation.warnings.length > 0 && (
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Avvisi</AlertTitle>
                      <AlertDescription>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          {validation.warnings.map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}

                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">
                      Consumo totale: {validation.power_budget_ma}mA
                    </p>
                  </div>

                  {Object.keys(validation.pin_assignments).length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Assegnazione pin</p>
                      <div className="bg-gray-50 rounded-lg p-3 space-y-1 max-h-48 overflow-y-auto">
                        {Object.entries(validation.pin_assignments).map(([label, pin]) => (
                          <div key={label} className="text-sm flex justify-between">
                            <span className="font-medium">{label}:</span>
                            <span className="text-gray-600">{pin}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {validation.valid && (
                    <Button onClick={handleGenerate} disabled={loading} className="w-full" size="lg">
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                          Generazione in corso...
                        </>
                      ) : (
                        <>
                          <Zap className="mr-2 h-5 w-5" />
                          Genera file KiCad
                        </>
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {step === 'generate' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                File generati con successo!
              </CardTitle>
              <CardDescription>
                Scarica i file e importali in KiCad per visualizzare lo schema
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {validation && (
                <Alert>
                  <CheckCircle2 className="h-4 w-4" />
                  <AlertTitle>Riepilogo</AlertTitle>
                  <AlertDescription>
                    <p>Componenti: {Object.keys(validation.pin_assignments).length}</p>
                    <p>Consumo totale: {validation.power_budget_ma}mA</p>
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-3">
                {Object.keys(files).map((fileKey) => (
                  <Button
                    key={fileKey}
                    onClick={() => downloadFile(fileKey)}
                    variant="outline"
                    className="w-full justify-between"
                  >
                    <span>{files[fileKey].filename}</span>
                    <Download className="h-4 w-4" />
                  </Button>
                ))}
              </div>

              <Button onClick={reset} className="w-full" size="lg">
                Crea un nuovo circuito
              </Button>
            </CardContent>
          </Card>
        )}

        <footer className="text-center py-8 text-sm text-gray-500">
          <p>Powered by OpenAI GPT-4 • ESP32 • KiCad</p>
        </footer>
      </div>
    </div>
  )
}

export default App
