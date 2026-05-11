import { useState } from 'react';

import { manualApi } from '../../error-search/infra/manual.api';
import { ApiError } from '../../../shared/api/apiError';
import { ManualSettingsPanel, type ManualUploadFormValues } from './ManualSettingsPanel';

const INITIAL_VALUES: ManualUploadFormValues = {
  title: '',
  category: '점검',
  version: 'v1.0',
  equipmentId: null,
  errorCodes: '',
  file: null,
};

function parseErrorCodes(raw: string): string[] {
  return raw
    .split(/[,\s]+/)
    .map((code) => code.trim())
    .filter((code) => code.length > 0);
}

type Props = {
  onUploadSuccess?: () => void;
};

export function AdminManualRegistration({ onUploadSuccess }: Props = {}) {
  const [values, setValues] = useState<ManualUploadFormValues>(INITIAL_VALUES);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async () => {
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!values.file) {
      setErrorMessage('PDF 파일을 선택해주세요.');
      return;
    }
    if (!values.title.trim()) {
      setErrorMessage('매뉴얼명을 입력해주세요.');
      return;
    }
    if (!values.version.trim()) {
      setErrorMessage('버전을 입력해주세요.');
      return;
    }
    // errorCodes는 비워도 OK — backend가 ai-service ingest 응답의 error_codes[]로 자동 매칭한다.
    const errorCodes = parseErrorCodes(values.errorCodes);

    setIsSubmitting(true);
    try {
      const result = await manualApi.upload({
        title: values.title.trim(),
        category: values.category,
        version: values.version.trim(),
        equipmentId: values.equipmentId,
        errorCodes,
        file: values.file,
      });
      setSuccessMessage(`업로드 완료: ${result.title} (manual_id=${result.manualId})`);
      setValues(INITIAL_VALUES);
      onUploadSuccess?.();
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401) setErrorMessage('로그인 정보가 만료되었습니다.');
        else if (error.status === 403) setErrorMessage('관리자 권한이 필요합니다.');
        else if (error.status === 422) setErrorMessage('입력 값을 다시 확인해주세요.');
        else setErrorMessage(error.message || '업로드 중 오류가 발생했습니다.');
      } else {
        setErrorMessage('업로드 중 오류가 발생했습니다.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ManualSettingsPanel
      values={values}
      onChange={setValues}
      onSubmit={handleSubmit}
      isSubmitting={isSubmitting}
      errorMessage={errorMessage}
      successMessage={successMessage}
    />
  );
}
