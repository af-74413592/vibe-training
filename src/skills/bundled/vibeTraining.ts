import { parseFrontmatter } from '../../utils/frontmatterParser.js'
import { parseSlashCommandToolsFromFrontmatter } from '../../utils/markdownConfigLoader.js'
import { registerBundledSkill } from '../bundledSkills.js'

import dataMd from './vibe-training/data.md' with { type: 'text' }
import detailMd from './vibe-training/detail.md' with { type: 'text' }
import evalMd from './vibe-training/eval.md' with { type: 'text' }
import inferMd from './vibe-training/infer.md' with { type: 'text' }
import modelingMd from './vibe-training/modeling.md' with { type: 'text' }
import planningMd from './vibe-training/planning.md' with { type: 'text' }
import preprocessMd from './vibe-training/preprocess.md' with { type: 'text' }
import rootMd from './vibe-training/SKILL.md' with { type: 'text' }
import trainMd from './vibe-training/train.md' with { type: 'text' }
import trainerMd from './vibe-training/trainer.md' with { type: 'text' }

import commonPy from '../../../runtime/vibe-training/common.py' with { type: 'text' }
import dataHelperPy from '../../../runtime/vibe-training/data_helper.py' with { type: 'text' }
import evalHelperPy from '../../../runtime/vibe-training/eval_helper.py' with { type: 'text' }
import inferHelperPy from '../../../runtime/vibe-training/infer_helper.py' with { type: 'text' }
import launchPy from '../../../runtime/vibe-training/launch.py' with { type: 'text' }
import readmeMd from '../../../runtime/vibe-training/README.md' with { type: 'text' }
import requirementsTxt from '../../../runtime/vibe-training/requirements.txt' with { type: 'text' }
import trainHelperPy from '../../../runtime/vibe-training/train_helper.py' with { type: 'text' }

type VibeSkillSource = {
  markdown: string
  includeRuntime?: boolean
}

const RUNTIME_FILES: Record<string, string> = {
  'runtime/README.md': readmeMd,
  'runtime/requirements.txt': requirementsTxt,
  'runtime/common.py': commonPy,
  'runtime/launch.py': launchPy,
  'runtime/data_helper.py': dataHelperPy,
  'runtime/train_helper.py': trainHelperPy,
  'runtime/eval_helper.py': evalHelperPy,
  'runtime/infer_helper.py': inferHelperPy,
}

const PHASE_FILES: Record<string, string> = {
  'phases/planning.md': planningMd,
  'phases/modeling.md': modelingMd,
  'phases/data.md': dataMd,
  'phases/detail.md': detailMd,
  'phases/preprocess.md': preprocessMd,
  'phases/trainer.md': trainerMd,
  'phases/train.md': trainMd,
  'phases/eval.md': evalMd,
  'phases/infer.md': inferMd,
}

const SKILLS: VibeSkillSource[] = [
  { markdown: rootMd, includeRuntime: true },
  { markdown: planningMd },
  { markdown: modelingMd },
  { markdown: dataMd },
  { markdown: detailMd },
  { markdown: preprocessMd, includeRuntime: true },
  { markdown: trainerMd, includeRuntime: true },
  { markdown: trainMd, includeRuntime: true },
  { markdown: evalMd, includeRuntime: true },
  { markdown: inferMd, includeRuntime: true },
]

function frontmatterString(value: unknown): string | undefined {
  return typeof value === 'string' ? value : undefined
}

function frontmatterBoolean(value: unknown, fallback: boolean): boolean {
  if (value === undefined) return fallback
  if (typeof value === 'boolean') return value
  if (typeof value === 'string') {
    return value.toLowerCase() === 'true'
  }
  return fallback
}

function registerMarkdownBundledSkill({
  markdown,
  includeRuntime,
}: VibeSkillSource): void {
  const { frontmatter, content } = parseFrontmatter(markdown)
  const name = frontmatterString(frontmatter.name)
  const description = frontmatterString(frontmatter.description)

  if (!name || !description) {
    throw new Error('Bundled vibe-training skill requires name and description')
  }

  const files = includeRuntime
    ? {
        ...PHASE_FILES,
        ...RUNTIME_FILES,
      }
    : PHASE_FILES

  registerBundledSkill({
    name,
    description,
    allowedTools: parseSlashCommandToolsFromFrontmatter(
      frontmatter['allowed-tools'],
    ),
    whenToUse: frontmatterString(frontmatter.when_to_use),
    userInvocable: frontmatterBoolean(frontmatter['user-invocable'], true),
    context: frontmatter.context === 'fork' ? 'fork' : 'inline',
    agent: frontmatterString(frontmatter.agent),
    files,
    async getPromptForCommand(args) {
      const parts = [content.trimStart()]
      if (args) {
        parts.push(`## User Request\n\n${args}`)
      }
      return [{ type: 'text', text: parts.join('\n\n') }]
    },
  })
}

export function registerVibeTrainingSkill(): void {
  for (const skill of SKILLS) {
    registerMarkdownBundledSkill(skill)
  }
}
