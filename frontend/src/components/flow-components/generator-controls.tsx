"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { UseMutateFunction } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useShallow } from "zustand/react/shallow";
import { useUIStore } from "@/lib/stores";
import GenerateButton from "@/components/flow-components/generate-button";
import ModelSelect from "@/components/flow-components/model-select";

interface Props {
  title?: string;
  isPending: boolean;
  renderFlow: string;
  mutate: UseMutateFunction<any, AxiosError<unknown, any>, any, unknown>;
}

export const GeneratorControls = (props: Props) => {
  const {
    title,
    mutate,
    isPending,
    renderFlow,
  } = props;
  const [isGenerating, setIsGenerating] = useState(false);

  const { model, query, setModelApiKey, setQuery, modelApiKey } = useUIStore(
    useShallow((state) => ({
      model: state.model,
      query: state.query,
      modelApiKey: state.modelApiKey,
      setModelApiKey: state.setModelApiKey,
      setQuery: state.setQuery,
    })),
  );

  useEffect(() => {
    const storedKey = localStorage.getItem(`${model.toUpperCase()}_API_KEY`);
    if (storedKey != null && storedKey !== "") {
      setModelApiKey(storedKey);
    }
  }, [model, setModelApiKey]);

  const onSubmit = async (
    e:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.FormEvent<HTMLFormElement>
      | React.KeyboardEvent<HTMLInputElement>,
  ) => {
    e.preventDefault();
    try {
      setIsGenerating(true);
      if (!query) {
        return toast.error("Please enter a query", {
          description: "We need a query to generate a roadmap.",
          duration: 4000,
        });
      }

      toast.info("Generating roadmap", {
        description: "We are generating a roadmap for you.",
        duration: 4000,
      });

      mutate(
        {
          body: { query },
        },
        {
          onSuccess: () => {
            toast.success("Success", {
              description: "Roadmap generated successfully.",
              duration: 4000,
            });
          },
          onError: (error: any) => {
            const data = error.response?.data;
            const description =
              data?.detail ||
              data?.message ||
              "Unknown error occurred";
            toast.error("Something went wrong", {
              description,
              duration: 8000,
            });
          },
        },
      );
    } catch (e: any) {
      console.error("api error", e);
    } finally {
      setIsGenerating(false);
    }
  };

  const disableUI = isGenerating || isPending;

  return (
    <div className="container flex flex-col items-start justify-between space-y-2 py-4 sm:flex-row sm:items-center sm:space-y-0 md:h-16">
      <div className="md:mx-14 flex w-full space-x-2 sm:justify-end">
        {(
          <Input
            type="text"
            disabled={disableUI}
            placeholder="e.g. Try searching for Frontend or Backend"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSubmit(e);
              }
            }}
          />
        )}

        <div className="">
          <ModelSelect disabled={disableUI} />
        </div>

        <GenerateButton onClick={onSubmit} disabled={disableUI} />
      </div>
    </div>
  );
};
