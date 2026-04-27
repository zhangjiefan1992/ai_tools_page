import type { Root, Element, ElementContent } from 'hast';

export interface AdInjectorOptions {
  paragraphInterval?: number;
  maxAds?: number;
  minParagraphs?: number;
  placeholderClass?: string;
}

const DEFAULT_OPTIONS: Required<AdInjectorOptions> = {
  paragraphInterval: 3,
  maxAds: 3,
  minParagraphs: 6,
  placeholderClass: 'ad-injection-point',
};

export default function rehypeAdInjector(userOptions: AdInjectorOptions = {}) {
  const options = { ...DEFAULT_OPTIONS, ...userOptions };

  return (tree: Root) => {
    const rootChildren = tree.children;
    const paragraphIndices: number[] = [];

    rootChildren.forEach((node, index) => {
      if (isElementNode(node) && node.tagName === 'p') {
        paragraphIndices.push(index);
      }
    });

    if (paragraphIndices.length < options.minParagraphs) {
      return;
    }

    const adPositions: number[] = [];
    let adCount = 0;

    for (let i = options.paragraphInterval; i < paragraphIndices.length; i += options.paragraphInterval) {
      if (adCount >= options.maxAds) break;
      const insertAfterIndex = paragraphIndices[i - 1];
      adPositions.push(insertAfterIndex);
      adCount++;
    }

    for (let i = adPositions.length - 1; i >= 0; i--) {
      const insertIndex = adPositions[i] + 1;
      const adPlaceholder: Element = {
        type: 'element',
        tagName: 'div',
        properties: {
          className: [options.placeholderClass],
          'data-ad-index': String(i),
        },
        children: [],
      };

      rootChildren.splice(insertIndex, 0, adPlaceholder as ElementContent);
    }
  };
}

function isElementNode(node: any): node is Element {
  return node.type === 'element';
}
